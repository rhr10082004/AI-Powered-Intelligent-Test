"""Adaptive mock test generation, grading, history and section/topic trends."""

from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from services.api.activity import record_activity
from services.api.database import get_db_session
from services.api.models import User
from services.api.models_phase2_isolated import (
    Answer, ListeningTrack, MockTestAttempt, Passage, Question, StudySession,
    UserAnswer, listening_questions, passage_questions,
)
from services.api.schemas_phase2 import QuestionPracticeResponse
from services.api.utils.auth import verify_token

router = APIRouter(prefix="/mock-tests", tags=["mock tests"])
AsyncSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


class MockTestStartRequest(BaseModel):
    exam_type: str = Field(min_length=2, max_length=50)
    question_count: int = Field(default=10, ge=6, le=30)


class MockTestStartResponse(BaseModel):
    attempt_id: UUID
    exam_type: str
    question_count: int
    adaptive_level: str
    questions: list[QuestionPracticeResponse]


class MockTestAnswer(BaseModel):
    question_id: UUID
    answer_id: UUID


class MockTestSubmitRequest(BaseModel):
    attempt_id: UUID
    answers: list[MockTestAnswer]
    duration: int = Field(default=0, ge=0, le=86400)


class MockTestResult(BaseModel):
    id: UUID
    exam_type: str
    question_count: int
    correct_count: int
    accuracy: float
    adaptive_level: str
    section_scores: dict
    topic_scores: dict
    score_label: str
    created_at: datetime


class MockTestHistoryItem(BaseModel):
    id: UUID
    exam_type: str
    question_count: int
    correct_count: int
    accuracy: float
    adaptive_level: str
    section_scores: dict
    topic_scores: dict
    score_label: str
    created_at: datetime


async def _learner(db: AsyncSession, token: str) -> UUID:
    user_id = verify_token(token, "access")
    if not user_id or await db.get(User, user_id) is None:
        raise HTTPException(status_code=401, detail="Sign in to start a mock test.")
    return user_id


def _label(accuracy: float) -> str:
    if accuracy >= 85:
        return "Strong"
    if accuracy >= 65:
        return "Developing"
    if accuracy >= 40:
        return "Building"
    return "Starting"


async def _questions_for_section(db: AsyncSession, exam: str, section: str, count: int, difficulty: str | None = None, excluded: set[UUID] | None = None) -> list[Question]:
    query = select(Question).options(selectinload(Question.answers)).where(Question.exam_type == exam, Question.section == section)
    if difficulty:
        query = query.where(Question.difficulty == difficulty)
    if excluded:
        query = query.where(Question.id.not_in(excluded))
    result = await db.execute(query.order_by(func.random()).limit(count))
    return list(result.scalars().all())


@router.post("/start", response_model=MockTestStartResponse)
async def start_mock_test(payload: MockTestStartRequest, token: str = Query(...), db: AsyncSession = Depends(get_db_session)) -> MockTestStartResponse:
    user_id = await _learner(db, token)
    exam = payload.exam_type.strip().upper()
    if exam not in {"IELTS", "TOEFL", "GRE"}:
        raise HTTPException(status_code=422, detail="Choose IELTS, TOEFL, or GRE.")

    recent_result = await db.execute(
        select(UserAnswer.is_correct)
        .join(Question, Question.id == UserAnswer.question_id)
        .where(UserAnswer.user_id == user_id, Question.exam_type == exam, UserAnswer.is_correct.is_not(None))
        .order_by(UserAnswer.created_at.desc()).limit(20)
    )
    recent = [bool(value) for value in recent_result.scalars().all()]
    recent_accuracy = sum(recent) / len(recent) if recent else None
    target_difficulty = "hard" if recent_accuracy is not None and recent_accuracy >= 0.8 else "easy" if recent_accuracy is not None and recent_accuracy < 0.4 else "medium"

    reading_count = (payload.question_count + 1) // 2
    listening_count = payload.question_count - reading_count
    questions: list[Question] = []
    for section, count in (("reading", reading_count), ("listening", listening_count)):
        if count <= 0:
            continue
        focused_count = max(1, count // 2)
        focused = await _questions_for_section(db, exam, section, focused_count, target_difficulty)
        selected = list(focused)
        selected_ids = {item.id for item in selected}
        selected.extend(await _questions_for_section(db, exam, section, count - len(selected), excluded=selected_ids))
        if len(selected) < count:
            raise HTTPException(status_code=409, detail=f"Not enough {section} questions are available for this exam yet.")
        questions.extend(selected)

    if len(questions) != payload.question_count:
        raise HTTPException(status_code=409, detail="This exam does not have enough questions for the selected mock test length.")

    attempt = MockTestAttempt(id=uuid4(), user_id=user_id, exam_type=exam, question_ids=[str(item.id) for item in questions], adaptive_level=target_difficulty, responses={}, section_scores={}, topic_scores={}, question_count=len(questions), created_at=datetime.utcnow())
    db.add(attempt)
    await db.commit()
    return MockTestStartResponse(attempt_id=attempt.id, exam_type=exam, question_count=len(questions), adaptive_level=target_difficulty, questions=[QuestionPracticeResponse.model_validate(question) for question in questions])


@router.post("/submit", response_model=MockTestResult)
async def submit_mock_test(payload: MockTestSubmitRequest, token: str = Query(...), db: AsyncSession = Depends(get_db_session)) -> MockTestResult:
    user_id = await _learner(db, token)
    attempt = await db.scalar(select(MockTestAttempt).where(MockTestAttempt.id == payload.attempt_id, MockTestAttempt.user_id == user_id))
    if attempt is None:
        raise HTTPException(status_code=404, detail="Mock test attempt not found.")
    if attempt.completed_at is not None:
        raise HTTPException(status_code=409, detail="This mock test has already been submitted.")

    question_ids = {UUID(value) for value in attempt.question_ids}
    answer_question_ids = [answer.question_id for answer in payload.answers]
    if len(answer_question_ids) != len(question_ids) or set(answer_question_ids) != question_ids or len(set(answer_question_ids)) != len(answer_question_ids):
        raise HTTPException(status_code=422, detail="Submit one answer for every question in this mock test.")

    questions_result = await db.execute(select(Question).where(Question.id.in_(question_ids)))
    questions = {question.id: question for question in questions_result.scalars().all()}
    if set(questions) != question_ids:
        raise HTTPException(status_code=409, detail="One or more questions are no longer available.")
    answer_ids = [item.answer_id for item in payload.answers]
    option_result = await db.execute(select(Answer).where(Answer.id.in_(answer_ids)))
    options = {option.id: option for option in option_result.scalars().all()}
    for item in payload.answers:
        option = options.get(item.answer_id)
        if option is None or option.question_id != item.question_id:
            raise HTTPException(status_code=400, detail="An answer option does not belong to its question.")

    correct_count = 0
    section_counts: dict[str, dict[str, int]] = {}
    topic_counts: dict[str, dict[str, int]] = {}
    response_map: dict[str, dict[str, object]] = {}
    questions_with_topics: dict[UUID, str] = {}
    passage_topics = await db.execute(select(passage_questions.c.question_id, Passage.topic).join(Passage, Passage.id == passage_questions.c.passage_id).where(passage_questions.c.question_id.in_(question_ids)))
    for question_id, topic in passage_topics.all():
        if topic:
            questions_with_topics[question_id] = topic
    track_topics = await db.execute(select(listening_questions.c.question_id, ListeningTrack.topic).join(ListeningTrack, ListeningTrack.id == listening_questions.c.track_id).where(listening_questions.c.question_id.in_(question_ids)))
    for question_id, topic in track_topics.all():
        if topic:
            questions_with_topics[question_id] = topic

    now = datetime.utcnow()
    for item in payload.answers:
        question = questions[item.question_id]
        option = options[item.answer_id]
        correct = bool(option.is_correct)
        correct_count += int(correct)
        section_bucket = section_counts.setdefault(question.section, {"correct": 0, "total": 0})
        section_bucket["correct"] += int(correct)
        section_bucket["total"] += 1
        topic = questions_with_topics.get(question.id, question.section.title())
        topic_bucket = topic_counts.setdefault(topic, {"correct": 0, "total": 0})
        topic_bucket["correct"] += int(correct)
        topic_bucket["total"] += 1
        response_map[str(question.id)] = {"answer_id": str(option.id), "correct": correct}
        previous_attempts = await db.scalar(select(func.count(UserAnswer.id)).where(UserAnswer.user_id == user_id, UserAnswer.question_id == question.id)) or 0
        db.add(UserAnswer(id=uuid4(), user_id=user_id, question_id=question.id, answer_id=option.id, is_correct=correct, attempts=previous_attempts + 1, session_id=attempt.id, created_at=now, updated_at=now))

    accuracy = round(correct_count / attempt.question_count, 4)
    section_scores = {section: {**values, "accuracy": round(values["correct"] / values["total"] * 100, 1)} for section, values in section_counts.items()}
    topic_scores = {topic: {**values, "accuracy": round(values["correct"] / values["total"] * 100, 1)} for topic, values in topic_counts.items()}
    attempt.responses = response_map
    attempt.correct_count = correct_count
    attempt.accuracy = accuracy
    attempt.section_scores = section_scores
    attempt.topic_scores = topic_scores
    attempt.completed_at = now
    db.add(StudySession(id=uuid4(), user_id=user_id, exam_id=None, session_id=attempt.id, section="mock_test", session_date=now, duration=payload.duration, questions_attempted=attempt.question_count, questions_correct=correct_count, accuracy=accuracy, score=accuracy * 100, notes=f"{attempt.exam_type} adaptive mock test"))
    record_activity(db, user_id=user_id, event_type="mock_test_completed", event_key=f"mock-test:{attempt.id}", section="mock_test", reference_id=attempt.id, details={"exam_type": attempt.exam_type, "accuracy": accuracy, "question_count": attempt.question_count}, points=10)
    await db.commit()
    return MockTestResult(id=attempt.id, exam_type=attempt.exam_type, question_count=attempt.question_count, correct_count=correct_count, accuracy=round(accuracy * 100, 1), adaptive_level=attempt.adaptive_level, section_scores=section_scores, topic_scores=topic_scores, score_label=_label(accuracy * 100), created_at=attempt.completed_at)


@router.get("/history", response_model=list[MockTestHistoryItem])
async def mock_test_history(token: str = Query(...), limit: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db_session)) -> list[MockTestHistoryItem]:
    user_id = await _learner(db, token)
    result = await db.execute(select(MockTestAttempt).where(MockTestAttempt.user_id == user_id, MockTestAttempt.completed_at.is_not(None)).order_by(MockTestAttempt.completed_at.desc()).limit(limit))
    return [MockTestHistoryItem(id=item.id, exam_type=item.exam_type, question_count=item.question_count, correct_count=item.correct_count, accuracy=round((item.accuracy or 0) * 100, 1), adaptive_level=item.adaptive_level, section_scores=item.section_scores, topic_scores=item.topic_scores, score_label=_label((item.accuracy or 0) * 100), created_at=item.completed_at or item.created_at) for item in result.scalars().all()]
