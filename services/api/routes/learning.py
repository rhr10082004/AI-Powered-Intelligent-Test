"""Phase 2 API routes for learning content."""

import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, func
from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from services.api.database import get_db_session
from services.api.activity import record_activity
from services.api.config import get_settings
from services.api.models_phase2_isolated import (
    Question, Answer, UserAnswer, Passage,
    ListeningTrack, VocabularyWord, UserVocabulary,
    GrammarTopic, GrammarExercise, GrammarAttempt, StudySession, UserProgress, DailyStudyPlan
)

from services.api.schemas_phase2 import (
    QuestionResponse, QuestionPracticeResponse, QuestionCreate, QuestionListResponse,
    UserAnswerCreate, UserAnswerResponse, PracticeAnswerResult,
    PassageResponse, PassageCreate, PassageWithQuestionsResponse,
    ListeningTrackResponse, ListeningTrackCreate,
    ListeningTrackWithQuestionsResponse,
    VocabularyWordResponse, VocabularyWordCreate,
    UserVocabularyResponse, UserVocabularyUpdate,
    GrammarTopicResponse, GrammarExerciseResponse,
    GrammarTopicPracticeResponse,
    GrammarExerciseAnswerSubmit,
    GrammarAnswerResult, GrammarAttemptHistoryItem,
    StudySessionCreate, StudySessionComplete, StudySessionResponse,
    UserProgressResponse, ProgressSummary, StudyRecommendation,
    AchievementResponse,
)
from services.api.utils.auth import verify_token
from services.api.models import User, UserExam

router = APIRouter(tags=["learning"])


class DailyPlanTask(BaseModel):
    id: str
    title: str
    section: str
    minutes: int = Field(ge=1, le=180)
    href: str
    completed: bool = False


class DailyPlanResponse(BaseModel):
    id: UUID
    exam_type: str
    plan_date: datetime
    target_minutes: int
    tasks: list[DailyPlanTask]
    created_at: datetime

    class Config:
        from_attributes = True


class DailyPlanRequest(BaseModel):
    exam_type: Optional[str] = Field(default="GENERAL", min_length=2, max_length=50)


class DiagnosticQuestionSet(BaseModel):
    exam_type: str
    section: str
    question_count: int
    questions: list[QuestionPracticeResponse]


async def require_content_admin(
    x_admin_token: Optional[str] = Header(None, alias="X-Admin-Token"),
) -> None:
    """Protect content mutations and deny them when no admin key is configured."""
    expected_token = get_settings().admin_api_key
    if not expected_token or not x_admin_token or not hmac.compare_digest(x_admin_token, expected_token):
        raise HTTPException(status_code=403, detail="Content administration is not authorized")


# ============================================================================
# Question Endpoints
# ============================================================================

@router.get("/questions", response_model=List[QuestionListResponse])
async def list_questions(
    exam_type: Optional[str] = Query(None),
    section: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session)
) -> List[QuestionListResponse]:
    """List questions with optional filters."""
    query = select(Question)
    
    # Apply filters
    filters = []
    if exam_type:
        filters.append(Question.exam_type == exam_type)
    if section:
        filters.append(Question.section == section)
    if difficulty:
        filters.append(Question.difficulty == difficulty)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Paginate
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    questions = result.scalars().all()
    return questions


@router.get("/questions/{question_id}", response_model=QuestionPracticeResponse)
async def get_question(
    question_id: UUID,
    db: AsyncSession = Depends(get_db_session)
) -> QuestionPracticeResponse:
    """Get a practice question without exposing its answer key."""
    result = await db.execute(
        select(Question)
        .options(selectinload(Question.answers))
        .where(Question.id == question_id)
    )
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return question


@router.get("/diagnostic/questions", response_model=DiagnosticQuestionSet)
async def get_diagnostic_questions(
    exam_type: str = Query(..., min_length=2, max_length=50),
    token: str = Query(...),
    limit: int = Query(5, ge=3, le=10),
    db: AsyncSession = Depends(get_db_session),
) -> DiagnosticQuestionSet:
    """Choose a short, answer-key-safe reading baseline from the learner's exam bank."""
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    normalized_exam = exam_type.strip().upper()
    if normalized_exam not in {"IELTS", "GRE", "TOEFL"}:
        raise HTTPException(status_code=422, detail="Supported exams are IELTS, GRE, and TOEFL")
    result = await db.execute(
        select(Question)
        .options(selectinload(Question.answers))
        .where(Question.exam_type == normalized_exam, Question.section == "reading")
        .order_by(func.random())
        .limit(limit)
    )
    questions = list(result.scalars().all())
    if len(questions) < 3:
        raise HTTPException(status_code=409, detail="This exam does not yet have enough questions for a diagnostic")
    return DiagnosticQuestionSet(
        exam_type=normalized_exam,
        section="reading",
        question_count=len(questions),
        questions=questions,
    )


@router.post("/questions", response_model=QuestionResponse, status_code=201)
async def create_question(
    question: QuestionCreate,
    db: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_content_admin),
) -> QuestionResponse:
    """Create a question using the configured administrative token."""
    db_question = Question(
        text=question.text,
        exam_type=question.exam_type,
        section=question.section,
        subsection=question.subsection,
        question_type=question.question_type,
        difficulty=question.difficulty,
        explanation=question.explanation,
        time_limit=question.time_limit,
        audio_url=question.audio_url,
        image_url=question.image_url,
        tags=question.tags,
        source=question.source
    )
    
    # Add answers
    for answer in question.answers:
        db_answer = Answer(
            text=answer.text,
            is_correct=answer.is_correct,
            explanation=answer.explanation,
            order=answer.order
        )
        db_question.answers.append(db_answer)
    
    db.add(db_question)
    await db.commit()
    await db.refresh(db_question)
    
    return db_question


# ============================================================================
# User Answer Endpoints
# ============================================================================

@router.post("/questions/answer", response_model=PracticeAnswerResult)
async def submit_answer(
    answer: UserAnswerCreate,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db_session)
) -> PracticeAnswerResult:
    """Submit an answer to a question."""
    # Verify user token
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get question
    result = await db.execute(
        select(Question).where(Question.id == answer.question_id)
    )
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if answer is correct
    answer_obj = None
    is_correct = None
    if answer.answer_id:
        result = await db.execute(
            select(Answer).where(
                and_(
                    Answer.id == answer.answer_id,
                    Answer.question_id == question.id,
                )
            )
        )
        answer_obj = result.scalar_one_or_none()
        if not answer_obj:
            raise HTTPException(status_code=400, detail="Answer option does not belong to this question")
        is_correct = answer_obj.is_correct

    # A retried request for the same question in one finalized practice set is idempotent.
    if answer.session_id:
        existing_attempt = await db.scalar(
            select(UserAnswer).where(
                and_(UserAnswer.user_id == user_id,
                     UserAnswer.question_id == question.id,
                     UserAnswer.session_id == answer.session_id)
            )
        )
        if existing_attempt:
            saved_option = await db.get(Answer, existing_attempt.answer_id) if existing_attempt.answer_id else None
            return PracticeAnswerResult(
                id=existing_attempt.id,
                question_id=question.id,
                is_correct=existing_attempt.is_correct,
                correct_answer=saved_option.text if saved_option and not existing_attempt.is_correct else None,
                explanation=(saved_option.explanation if saved_option and saved_option.explanation else question.explanation),
                attempts=existing_attempt.attempts,
            )

    attempts_result = await db.execute(
        select(func.count(UserAnswer.id)).where(
            and_(UserAnswer.user_id == user_id, UserAnswer.question_id == question.id)
        )
    )
    attempts = attempts_result.scalar_one() + 1
    
    # Create user answer record
    db_user_answer = UserAnswer(
        id=uuid4(),
        user_id=user_id,
        question_id=answer.question_id,
        answer_id=answer.answer_id,
        user_text_answer=answer.user_text_answer,
        is_correct=is_correct,
        time_taken=answer.time_taken,
        attempts=attempts,
        session_id=answer.session_id,
    )
    db.add(db_user_answer)
    record_activity(
        db,
        user_id=user_id,
        event_type="question_answered",
        event_key=f"answer:{db_user_answer.id}",
        section=question.section,
        reference_id=db_user_answer.id,
        details={"correct": is_correct is True},
        points=1,
    )
    await db.commit()
    await db.refresh(db_user_answer)
    
    enrollment_result = await db.execute(
        select(UserExam).where(
            and_(UserExam.user_id == user_id, UserExam.is_active.is_(True))
        )
    )
    exam = next(
        (
            item
            for item in enrollment_result.scalars().all()
            if item.exam_type.value.casefold() == question.exam_type.casefold()
        ),
        None,
    )
    if exam:
        practiced_at = datetime.utcnow()
        progress_result = await db.execute(
            select(UserProgress).where(
                and_(
                    UserProgress.user_id == user_id,
                    UserProgress.exam_id == exam.id,
                    UserProgress.section == question.section,
                )
            )
        )
        progress = progress_result.scalar_one_or_none()
        if progress is None:
            progress = UserProgress(
                user_id=user_id,
                exam_id=exam.id,
                section=question.section,
                total_questions=1,
                correct_answers=int(is_correct is True),
                last_practiced=practiced_at,
                study_streak=1,
            )
            db.add(progress)
        else:
            progress.total_questions += 1
            progress.correct_answers += int(is_correct is True)
            if progress.last_practiced is None:
                progress.study_streak = 1
            else:
                days_since_last_practice = (practiced_at.date() - progress.last_practiced.date()).days
                if days_since_last_practice == 1:
                    progress.study_streak += 1
                elif days_since_last_practice > 1:
                    progress.study_streak = 1
            progress.last_practiced = practiced_at
        progress.accuracy = progress.correct_answers / progress.total_questions
        await db.commit()

    return PracticeAnswerResult(
        id=db_user_answer.id,
        question_id=question.id,
        is_correct=is_correct,
        correct_answer=answer_obj.text if answer_obj and not is_correct else None,
        explanation=(answer_obj.explanation if answer_obj and answer_obj.explanation else question.explanation),
        attempts=attempts,
    )


@router.post("/study-sessions/complete", response_model=StudySessionResponse)
async def complete_study_session(
    completion: StudySessionComplete,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db_session),
) -> StudySessionResponse:
    """Finalize one submitted practice set and save its aggregate result."""
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    existing_result = await db.execute(
        select(StudySession).where(
            and_(
                StudySession.user_id == user_id,
                StudySession.session_id == completion.session_id,
            )
        )
    )
    existing_session = existing_result.scalar_one_or_none()
    if existing_session:
        return existing_session

    answer_result = await db.execute(
        select(UserAnswer).where(
            and_(
                UserAnswer.user_id == user_id,
                UserAnswer.session_id == completion.session_id,
            )
        )
    )
    submitted_answers = list(answer_result.scalars().all())
    if not submitted_answers:
        raise HTTPException(status_code=400, detail="No answers were submitted for this session")

    question_ids = {item.question_id for item in submitted_answers}
    questions_result = await db.execute(
        select(Question).where(Question.id.in_(question_ids))
    )
    questions = list(questions_result.scalars().all())
    sections = {question.section for question in questions}
    exam_types = {question.exam_type.casefold() for question in questions}
    if sections != {completion.section} or len(exam_types) != 1:
        raise HTTPException(status_code=400, detail="Session answers must belong to one section and exam")

    enrollments_result = await db.execute(
        select(UserExam).where(
            and_(UserExam.user_id == user_id, UserExam.is_active.is_(True))
        )
    )
    matching_exam = next(
        (
            item
            for item in enrollments_result.scalars().all()
            if item.exam_type.value.casefold() in exam_types
        ),
        None,
    )
    correct_count = sum(item.is_correct is True for item in submitted_answers)
    session = StudySession(
        id=uuid4(),
        user_id=user_id,
        exam_id=matching_exam.id if matching_exam else None,
        session_id=completion.session_id,
        section=completion.section,
        duration=completion.duration,
        questions_attempted=len(submitted_answers),
        questions_correct=correct_count,
        accuracy=correct_count / len(submitted_answers),
    )
    db.add(session)
    record_activity(
        db,
        user_id=user_id,
        event_type="study_session_completed",
        event_key=f"study-session:{completion.session_id}",
        section=completion.section,
        reference_id=session.id,
        details={"questions": len(submitted_answers), "correct": correct_count},
        points=5,
    )
    await db.commit()
    await db.refresh(session)
    return session


@router.get("/study-sessions/my-sessions", response_model=List[StudySessionResponse])
async def get_my_study_sessions(
    token: str = Query(...),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session),
) -> List[StudySessionResponse]:
    """Return recent finalized study sessions for the authenticated user."""
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    result = await db.execute(
        select(StudySession)
        .where(StudySession.user_id == user_id)
        .order_by(StudySession.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


@router.get("/progress/my-summary", response_model=List[UserProgressResponse])
async def get_my_progress_summary(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db_session),
) -> List[UserProgressResponse]:
    """Return the signed-in learner's progress grouped by exam and section."""
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(
        select(UserProgress)
        .where(UserProgress.user_id == user_id)
        .order_by(UserProgress.last_practiced.desc())
    )
    return list(result.scalars().all())


@router.get("/study-plan/recommendations", response_model=List[StudyRecommendation])
async def get_study_recommendations(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db_session),
) -> List[StudyRecommendation]:
    """Recommend the least-practiced or lowest-accuracy enrolled skill."""
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(
        select(UserProgress).where(UserProgress.user_id == user_id)
    )
    progress_rows = list(result.scalars().all())
    if not progress_rows:
        return [
            StudyRecommendation(
                section="reading",
                title="Start with a reading diagnostic",
                reason="A short practice set gives your study plan a useful baseline.",
                href="/practice/reading",
            ),
            StudyRecommendation(
                section="listening",
                title="Try a listening practice set",
                reason="Build familiarity with question types before timed practice.",
                href="/practice/listening",
            ),
        ]

    weakest = min(
        progress_rows,
        key=lambda item: (
            item.accuracy if item.accuracy is not None else 0,
            item.total_questions,
        ),
    )
    section_links = {
        "reading": ("Reading practice", "/practice/reading"),
        "listening": ("Listening practice", "/practice/listening"),
        "grammar": ("Grammar exercises", "/practice/grammar"),
        "vocabulary": ("Vocabulary review", "/practice/vocabulary"),
    }
    title, href = section_links.get(
        weakest.section,
        (f"Practice {weakest.section}", "/practice"),
    )
    accuracy_percent = round((weakest.accuracy or 0) * 100)
    return [
        StudyRecommendation(
            section=weakest.section,
            title=f"Focus next: {title}",
            reason=f"This area is currently at {accuracy_percent}% accuracy across {weakest.total_questions} attempts.",
            href=href,
            accuracy_percent=accuracy_percent,
        )
    ]


@router.post("/study-plan/today", response_model=DailyPlanResponse)
async def ensure_daily_study_plan(
    payload: DailyPlanRequest,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db_session),
) -> DailyPlanResponse:
    """Return today's saved plan or generate a focused 30-minute plan once."""
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    now = datetime.utcnow()
    today = datetime(now.year, now.month, now.day)
    exam_type = (payload.exam_type or "GENERAL").upper()
    existing = await db.scalar(
        select(DailyStudyPlan).where(
            and_(DailyStudyPlan.user_id == user_id,
                 DailyStudyPlan.exam_type == exam_type,
                 DailyStudyPlan.plan_date == today)
        )
    )
    if existing:
        return existing

    progress = await db.execute(
        select(UserProgress).where(UserProgress.user_id == user_id)
    )
    rows = list(progress.scalars().all())
    if exam_type != "GENERAL":
        enrollments = await db.execute(
            select(UserExam).where(
                and_(UserExam.user_id == user_id, UserExam.is_active.is_(True))
            )
        )
        matching_ids = {
            item.id for item in enrollments.scalars().all()
            if item.exam_type.value.upper() == exam_type
        }
        rows = [row for row in rows if row.exam_id in matching_ids]
    focus = min(rows, key=lambda row: row.accuracy if row.accuracy is not None else 0) if rows else None
    section = focus.section if focus else "reading"
    section_routes = {
        "reading": ("Read one short passage", "/practice/reading"),
        "listening": ("Complete one listening set", "/practice/listening"),
        "grammar": ("Review one grammar lesson", "/practice/grammar"),
        "vocabulary": ("Review due vocabulary", "/practice/vocabulary"),
        "writing": ("Draft a short essay", "/practice/writing"),
    }
    focus_title, focus_href = section_routes.get(section, (f"Practice {section}", "/practice"))
    tasks = [
        {"id": str(uuid4()), "title": focus_title, "section": section, "minutes": 15, "href": focus_href, "completed": False},
        {"id": str(uuid4()), "title": "Strengthen your vocabulary", "section": "vocabulary", "minutes": 10, "href": "/practice/vocabulary", "completed": False},
        {"id": str(uuid4()), "title": "Reflect on one mistake", "section": "review", "minutes": 5, "href": "/dashboard", "completed": False},
    ]
    plan = DailyStudyPlan(
        user_id=user_id,
        exam_type=exam_type,
        plan_date=today,
        target_minutes=30,
        tasks=tasks,
        created_at=now,
        updated_at=now,
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


@router.get("/study-plan/today", response_model=DailyPlanResponse)
async def get_daily_study_plan(
    exam_type: str = Query("GENERAL", min_length=2, max_length=50),
    token: str = Query(...),
    db: AsyncSession = Depends(get_db_session),
) -> DailyPlanResponse:
    """Read today's plan without creating one."""
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    now = datetime.utcnow()
    today = datetime(now.year, now.month, now.day)
    plan = await db.scalar(
        select(DailyStudyPlan).where(
            and_(DailyStudyPlan.user_id == user_id,
                 DailyStudyPlan.exam_type == exam_type.upper(),
                 DailyStudyPlan.plan_date == today)
        )
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Today's study plan has not been generated")
    return plan


@router.post("/study-plan/{plan_id}/tasks/{task_id}/complete", response_model=DailyPlanResponse)
async def complete_daily_plan_task(
    plan_id: UUID,
    task_id: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db_session),
) -> DailyPlanResponse:
    """Mark one task complete on the authenticated learner's plan."""
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    plan = await db.scalar(
        select(DailyStudyPlan).where(
            and_(DailyStudyPlan.id == plan_id, DailyStudyPlan.user_id == user_id)
        )
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found")
    tasks = [dict(task) for task in plan.tasks]
    task = next((item for item in tasks if item.get("id") == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Plan task not found")
    already_completed = bool(task.get("completed"))
    task["completed"] = True
    plan.tasks = tasks
    plan.updated_at = datetime.utcnow()
    if not already_completed:
        record_activity(
            db,
            user_id=user_id,
            event_type="study_plan_task_completed",
            event_key=f"plan-task:{plan.id}:{task_id}",
            section=task.get("section"),
            reference_id=plan.id,
            details={"title": task.get("title", "Study plan task")},
            points=1,
        )
    await db.commit()
    await db.refresh(plan)
    return plan


@router.get("/achievements", response_model=List[AchievementResponse])
async def get_achievements(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db_session),
) -> List[AchievementResponse]:
    """Return achievement milestones derived from saved practice progress."""
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(
        select(UserProgress).where(UserProgress.user_id == user_id)
    )
    progress_rows = list(result.scalars().all())
    total_questions = sum(item.total_questions for item in progress_rows)
    best_streak = max((item.study_streak for item in progress_rows), default=0)
    milestones = (
        ("first-set", "First set", "Submit your first practice answer.", total_questions, 1),
        ("ten-answers", "Ten answers", "Record ten practice answers.", total_questions, 10),
        ("practice-streak", "Three-day streak", "Practice on three consecutive days.", best_streak, 3),
    )
    return [
        AchievementResponse(
            id=achievement_id,
            title=title,
            description=description,
            current=min(current, target),
            target=target,
            unlocked=current >= target,
        )
        for achievement_id, title, description, current, target in milestones
    ]


@router.get("/questions/my-answers", response_model=List[UserAnswerResponse])
async def get_my_answers(
    token: str = Query(...),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session)
) -> List[UserAnswerResponse]:
    """Get current user's answers."""
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    result = await db.execute(
        select(UserAnswer)
        .where(UserAnswer.user_id == user_id)
        .limit(limit)
        .offset(offset)
    )
    answers = result.scalars().all()
    return answers


# ============================================================================
# Passage Endpoints
# ============================================================================

@router.get("/passages", response_model=List[PassageResponse])
async def list_passages(
    exam_type: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=150),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session)
) -> List[PassageResponse]:
    """List reading passages."""
    query = select(Passage)
    
    filters = []
    if exam_type:
        filters.append(Passage.exam_type == exam_type)
    if difficulty:
        filters.append(Passage.difficulty == difficulty)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    passages = result.scalars().all()
    return passages


@router.get("/passages/{passage_id}", response_model=PassageWithQuestionsResponse)
async def get_passage(
    passage_id: UUID,
    db: AsyncSession = Depends(get_db_session)
) -> PassageWithQuestionsResponse:
    """Get a passage with related questions."""
    result = await db.execute(
        select(Passage)
        .options(selectinload(Passage.questions).selectinload(Question.answers))
        .where(Passage.id == passage_id)
    )
    passage = result.scalar_one_or_none()
    
    if not passage:
        raise HTTPException(status_code=404, detail="Passage not found")
    
    return passage


@router.post("/passages", response_model=PassageResponse, status_code=201)
async def create_passage(
    passage: PassageCreate,
    db: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_content_admin),
) -> PassageResponse:
    """Create a passage using the configured administrative token."""
    db_passage = Passage(
        title=passage.title,
        content=passage.content,
        word_count=passage.word_count,
        exam_type=passage.exam_type,
        difficulty=passage.difficulty,
        topic=passage.topic,
        source=passage.source,
        time_limit=passage.time_limit
    )
    
    db.add(db_passage)
    await db.commit()
    await db.refresh(db_passage)
    
    return db_passage


# ============================================================================
# Listening Endpoints
# ============================================================================

@router.get("/listening-tracks", response_model=List[ListeningTrackResponse])
async def list_listening_tracks(
    exam_type: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=150),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session)
) -> List[ListeningTrackResponse]:
    """List listening audio tracks."""
    query = select(ListeningTrack)
    
    filters = []
    if exam_type:
        filters.append(ListeningTrack.exam_type == exam_type)
    if difficulty:
        filters.append(ListeningTrack.difficulty == difficulty)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    tracks = result.scalars().all()
    return tracks


@router.get("/listening-tracks/{track_id}", response_model=ListeningTrackResponse)
async def get_listening_track(
    track_id: UUID,
    db: AsyncSession = Depends(get_db_session)
) -> ListeningTrackResponse:
    """Get a single listening track."""
    result = await db.execute(
        select(ListeningTrack).where(ListeningTrack.id == track_id)
    )
    track = result.scalar_one_or_none()
    
    if not track:
        raise HTTPException(status_code=404, detail="Listening track not found")
    
    return track


@router.get(
    "/listening-tracks/{track_id}/questions",
    response_model=List[QuestionPracticeResponse],
)
async def get_listening_track_questions(
    track_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> List[QuestionPracticeResponse]:
    """Return practice questions assigned to one listening track."""
    result = await db.execute(
        select(ListeningTrack)
        .options(selectinload(ListeningTrack.questions).selectinload(Question.answers))
        .where(ListeningTrack.id == track_id)
    )
    track = result.scalar_one_or_none()
    if not track:
        raise HTTPException(status_code=404, detail="Listening track not found")
    return list(track.questions)


@router.post("/listening-tracks", response_model=ListeningTrackResponse, status_code=201)
async def create_listening_track(
    track: ListeningTrackCreate,
    db: AsyncSession = Depends(get_db_session),
    _: None = Depends(require_content_admin),
) -> ListeningTrackResponse:
    """Create a listening track using the configured administrative token."""
    db_track = ListeningTrack(
        title=track.title,
        audio_url=track.audio_url,
        duration=track.duration,
        transcript=track.transcript,
        exam_type=track.exam_type,
        difficulty=track.difficulty,
        topic=track.topic,
        source=track.source,
        accent=track.accent,
        play_count=track.play_count
    )
    
    db.add(db_track)
    await db.commit()
    await db.refresh(db_track)
    
    return db_track


# ============================================================================
# Vocabulary Endpoints
# ============================================================================

@router.get("/vocabulary/words", response_model=List[VocabularyWordResponse])
async def list_vocabulary_words(
    exam_type: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=150),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session)
) -> List[VocabularyWordResponse]:
    """List vocabulary words."""
    query = select(VocabularyWord)
    
    filters = []
    if exam_type:
        filters.append(VocabularyWord.exam_type == exam_type)
    if difficulty:
        filters.append(VocabularyWord.difficulty == difficulty)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    words = result.scalars().all()
    return words


@router.get("/vocabulary/my-words", response_model=List[UserVocabularyResponse])
async def get_my_vocabulary(
    token: str = Query(...),
    proficiency: Optional[int] = Query(None, ge=1, le=5),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session)
) -> List[UserVocabularyResponse]:
    """Get current user's vocabulary."""
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    query = (
        select(UserVocabulary)
        .options(selectinload(UserVocabulary.word))
        .where(UserVocabulary.user_id == user_id)
    )
    
    if proficiency:
        query = query.where(UserVocabulary.proficiency_level == proficiency)
    
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    user_words = result.scalars().all()
    return user_words


@router.post("/vocabulary/add", response_model=UserVocabularyResponse)
async def add_vocabulary_word(
    word_id: UUID,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db_session)
) -> UserVocabularyResponse:
    """Add a vocabulary word to user's learning list."""
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Check if word exists
    result = await db.execute(
        select(VocabularyWord).where(VocabularyWord.id == word_id)
    )
    word = result.scalar_one_or_none()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    
    # Check if already added
    result = await db.execute(
        select(UserVocabulary)
        .options(selectinload(UserVocabulary.word))
        .where(
            and_(
                UserVocabulary.user_id == user_id,
                UserVocabulary.word_id == word_id
            )
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Word already in your list")
    
    # Add word
    db_user_word = UserVocabulary(
        user_id=user_id,
        word_id=word_id,
        proficiency_level=1,
        word=word,
    )
    
    db.add(db_user_word)
    await db.commit()
    result = await db.execute(
        select(UserVocabulary)
        .options(selectinload(UserVocabulary.word))
        .where(UserVocabulary.id == db_user_word.id)
    )
    return result.scalar_one()


@router.put("/vocabulary/{word_id}", response_model=UserVocabularyResponse)
async def update_vocabulary_proficiency(
    word_id: UUID,
    update: UserVocabularyUpdate,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db_session)
) -> UserVocabularyResponse:
    """Update word proficiency level."""
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    result = await db.execute(
        select(UserVocabulary)
        .options(selectinload(UserVocabulary.word))
        .where(
            and_(
                UserVocabulary.user_id == user_id,
                UserVocabulary.word_id == word_id
            )
        )
    )
    user_word = result.scalar_one_or_none()
    
    if not user_word:
        raise HTTPException(status_code=404, detail="Word not in your list")
    
    user_word.proficiency_level = update.proficiency_level
    user_word.review_count += 1
    user_word.last_reviewed = datetime.utcnow()
    review_intervals = (1, 3, 7, 14, 30)
    user_word.next_review = user_word.last_reviewed + timedelta(
        days=review_intervals[update.proficiency_level - 1]
    )
    
    await db.commit()
    result = await db.execute(
        select(UserVocabulary)
        .options(selectinload(UserVocabulary.word))
        .where(UserVocabulary.id == user_word.id)
    )
    return result.scalar_one()


# ============================================================================
# Grammar Endpoints
# ============================================================================

@router.get("/grammar/topics", response_model=List[GrammarTopicPracticeResponse])
async def list_grammar_topics(
    exam_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=150),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session)
) -> List[GrammarTopicPracticeResponse]:
    """List grammar topics."""
    query = select(GrammarTopic)
    
    if exam_type:
        query = query.where(GrammarTopic.exam_type == exam_type)
    
    query = query.options(selectinload(GrammarTopic.exercises))
    query = query.order_by(GrammarTopic.order).limit(limit).offset(offset)
    result = await db.execute(query)
    topics = result.scalars().all()
    return topics


@router.get("/grammar/topics/{topic_id}", response_model=GrammarTopicPracticeResponse)
async def get_grammar_topic(
    topic_id: UUID,
    db: AsyncSession = Depends(get_db_session)
) -> GrammarTopicPracticeResponse:
    """Get a grammar topic with exercises."""
    result = await db.execute(
        select(GrammarTopic)
        .options(selectinload(GrammarTopic.exercises))
        .where(GrammarTopic.id == topic_id)
    )
    topic = result.scalar_one_or_none()
    
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    return topic


@router.post("/grammar/exercises/answer", response_model=GrammarAnswerResult)
async def submit_grammar_answer(
    submission: GrammarExerciseAnswerSubmit,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """Submit a grammar exercise answer."""
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get exercise
    result = await db.execute(
        select(GrammarExercise).where(GrammarExercise.id == submission.exercise_id)
    )
    exercise = result.scalar_one_or_none()
    
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    # Check answer and persist the private attempt.
    is_correct = submission.user_answer.strip().lower() == exercise.correct_form.strip().lower()
    prior_attempts = await db.scalar(
        select(func.count(GrammarAttempt.id)).where(
            and_(GrammarAttempt.user_id == user_id, GrammarAttempt.exercise_id == exercise.id)
        )
    )
    attempt = GrammarAttempt(
        id=uuid4(),
        user_id=user_id,
        exercise_id=exercise.id,
        user_answer=submission.user_answer.strip(),
        is_correct=is_correct,
        created_at=datetime.utcnow(),
    )
    db.add(attempt)
    record_activity(
        db,
        user_id=user_id,
        event_type="grammar_attempted",
        event_key=f"grammar-attempt:{attempt.id}",
        section="grammar",
        reference_id=attempt.id,
        details={"correct": is_correct},
        points=1,
    )
    await db.commit()
    await db.refresh(attempt)

    return GrammarAnswerResult(
        id=attempt.id,
        exercise_id=exercise.id,
        is_correct=is_correct,
        correct_form=exercise.correct_form,
        explanation=exercise.explanation,
        attempt_number=(prior_attempts or 0) + 1,
        created_at=attempt.created_at,
    )


@router.get("/grammar/my-attempts", response_model=List[GrammarAttemptHistoryItem])
async def get_my_grammar_attempts(
    token: str = Query(...),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session),
) -> List[GrammarAttemptHistoryItem]:
    """Return recent grammar attempts owned by the authenticated learner."""
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(
        select(GrammarAttempt, GrammarExercise, GrammarTopic)
        .join(GrammarExercise, GrammarAttempt.exercise_id == GrammarExercise.id)
        .join(GrammarTopic, GrammarExercise.topic_id == GrammarTopic.id)
        .where(GrammarAttempt.user_id == user_id)
        .order_by(GrammarAttempt.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return [
        GrammarAttemptHistoryItem(
            id=attempt.id,
            exercise_id=exercise.id,
            topic_name=topic.topic_name,
            sentence=exercise.sentence,
            user_answer=attempt.user_answer,
            is_correct=attempt.is_correct,
            created_at=attempt.created_at,
        )
        for attempt, exercise, topic in result.all()
    ]


# ============================================================================
# Progress Endpoints
# ============================================================================

@router.get("/progress", response_model=ProgressSummary)
async def get_overall_progress(
    exam_id: UUID,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db_session)
) -> ProgressSummary:
    """Get user's overall progress for an exam."""
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    result = await db.execute(
        select(UserProgress).where(
            and_(
                UserProgress.user_id == user_id,
                UserProgress.exam_id == exam_id
            )
        )
    )
    progresses = result.scalars().all()
    
    sections = {}
    overall_accuracy = 0.0
    total_accuracy_count = 0
    
    for progress in progresses:
        sections[progress.section] = {
            "accuracy": progress.accuracy,
            "score": progress.average_score,
            "last_practiced": progress.last_practiced
        }
        if progress.accuracy:
            overall_accuracy += progress.accuracy
            total_accuracy_count += 1
    
    if total_accuracy_count > 0:
        overall_accuracy /= total_accuracy_count
    
    # Get study streak
    study_streak = progresses[0].study_streak if progresses else 0
    last_practiced = max(
        (p.last_practiced for p in progresses if p.last_practiced),
        default=None
    )
    
    return ProgressSummary(
        exam_id=exam_id,
        overall_accuracy=overall_accuracy,
        sections=sections,
        total_questions_answered=sum(p.total_questions for p in progresses),
        study_streak=study_streak,
        last_practiced=last_practiced
    )


@router.get("/progress/{exam_id}", response_model=List[UserProgressResponse])
async def get_exam_progress(
    exam_id: UUID,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db_session)
) -> List[UserProgressResponse]:
    """Get user's progress for a specific exam."""
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    result = await db.execute(
        select(UserProgress).where(
            and_(
                UserProgress.user_id == user_id,
                UserProgress.exam_id == exam_id
            )
        )
    )
    progresses = result.scalars().all()
    return progresses
