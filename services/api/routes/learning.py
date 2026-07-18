"""Phase 2 API routes for learning content."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from uuid import UUID
from typing import List, Optional

from services.api.database import get_db_session
from services.api.models_phase2_isolated import (
    Question, Answer, UserAnswer, Passage,
    ListeningTrack, VocabularyWord, UserVocabulary,
    GrammarTopic, GrammarExercise, StudySession, UserProgress
)

from services.api.schemas_phase2 import (
    QuestionResponse, QuestionCreate, QuestionListResponse,
    UserAnswerCreate, UserAnswerResponse,
    PassageResponse, PassageCreate, PassageWithQuestionsResponse,
    ListeningTrackResponse, ListeningTrackCreate,
    VocabularyWordResponse, VocabularyWordCreate,
    UserVocabularyResponse, UserVocabularyUpdate,
    GrammarTopicResponse, GrammarExerciseResponse,
    GrammarExerciseAnswerSubmit,
    StudySessionCreate, StudySessionResponse,
    UserProgressResponse, ProgressSummary
)
from services.api.utils.auth import verify_token
from services.api.models import User

router = APIRouter(prefix="/api", tags=["learning"])


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


@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: UUID,
    db: AsyncSession = Depends(get_db_session)
) -> QuestionResponse:
    """Get a single question with all answers."""
    result = await db.execute(
        select(Question).where(Question.id == question_id)
    )
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return question


@router.post("/questions", response_model=QuestionResponse, status_code=201)
async def create_question(
    question: QuestionCreate,
    db: AsyncSession = Depends(get_db_session)
) -> QuestionResponse:
    """Create a new question (admin only - add auth later)."""
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

@router.post("/questions/answer", response_model=UserAnswerResponse)
async def submit_answer(
    answer: UserAnswerCreate,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db_session)
) -> UserAnswerResponse:
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
    is_correct = False
    if answer.answer_id:
        result = await db.execute(
            select(Answer).where(Answer.id == answer.answer_id)
        )
        answer_obj = result.scalar_one_or_none()
        if answer_obj:
            is_correct = answer_obj.is_correct
    
    # Create user answer record
    db_user_answer = UserAnswer(
        user_id=user_id,
        question_id=answer.question_id,
        answer_id=answer.answer_id,
        user_text_answer=answer.user_text_answer,
        is_correct=is_correct,
        time_taken=answer.time_taken
    )
    
    db.add(db_user_answer)
    await db.commit()
    await db.refresh(db_user_answer)
    
    return db_user_answer


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
    limit: int = Query(10, ge=1, le=50),
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
        select(Passage).where(Passage.id == passage_id)
    )
    passage = result.scalar_one_or_none()
    
    if not passage:
        raise HTTPException(status_code=404, detail="Passage not found")
    
    return passage


@router.post("/passages", response_model=PassageResponse, status_code=201)
async def create_passage(
    passage: PassageCreate,
    db: AsyncSession = Depends(get_db_session)
) -> PassageResponse:
    """Create a new passage (admin)."""
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
    limit: int = Query(10, ge=1, le=50),
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


@router.post("/listening-tracks", response_model=ListeningTrackResponse, status_code=201)
async def create_listening_track(
    track: ListeningTrackCreate,
    db: AsyncSession = Depends(get_db_session)
) -> ListeningTrackResponse:
    """Create a new listening track (admin)."""
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
    limit: int = Query(20, ge=1, le=100),
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
    
    query = select(UserVocabulary).where(UserVocabulary.user_id == user_id)
    
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
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Word not found")
    
    # Check if already added
    result = await db.execute(
        select(UserVocabulary).where(
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
        proficiency_level=1
    )
    
    db.add(db_user_word)
    await db.commit()
    await db.refresh(db_user_word)
    
    return db_user_word


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
        select(UserVocabulary).where(
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
    
    await db.commit()
    await db.refresh(user_word)
    
    return user_word


# ============================================================================
# Grammar Endpoints
# ============================================================================

@router.get("/grammar/topics", response_model=List[GrammarTopicResponse])
async def list_grammar_topics(
    exam_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session)
) -> List[GrammarTopicResponse]:
    """List grammar topics."""
    query = select(GrammarTopic)
    
    if exam_type:
        query = query.where(GrammarTopic.exam_type == exam_type)
    
    query = query.order_by(GrammarTopic.order).limit(limit).offset(offset)
    result = await db.execute(query)
    topics = result.scalars().all()
    return topics


@router.get("/grammar/topics/{topic_id}", response_model=GrammarTopicResponse)
async def get_grammar_topic(
    topic_id: UUID,
    db: AsyncSession = Depends(get_db_session)
) -> GrammarTopicResponse:
    """Get a grammar topic with exercises."""
    result = await db.execute(
        select(GrammarTopic).where(GrammarTopic.id == topic_id)
    )
    topic = result.scalar_one_or_none()
    
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    return topic


@router.post("/grammar/exercises/answer", response_model=dict)
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
    
    # Check answer
    is_correct = submission.user_answer.strip().lower() == exercise.correct_form.strip().lower()
    
    return {
        "is_correct": is_correct,
        "correct_form": exercise.correct_form,
        "explanation": exercise.explanation
    }


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
