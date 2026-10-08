"""Phase 2 Pydantic schemas for validation."""

from pydantic import BaseModel, Field, constr
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime


# ============================================================================
# Question Schemas
# ============================================================================

class AnswerBase(BaseModel):
    """Base answer schema."""
    text: str = Field(..., min_length=1, max_length=1000)
    is_correct: bool
    explanation: Optional[str] = Field(None, max_length=2000)
    order: int


class AnswerCreate(AnswerBase):
    """Create answer schema."""
    pass


class AnswerResponse(AnswerBase):
    """Answer response schema."""
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuestionBase(BaseModel):
    """Base question schema."""
    text: str = Field(..., min_length=10, max_length=5000)
    exam_type: str = Field(..., min_length=1)  # IELTS, GRE, TOEFL
    section: str = Field(..., min_length=1)  # reading, listening, writing, speaking
    subsection: Optional[str] = Field(None, max_length=100)
    question_type: str = Field(..., min_length=1)  # MCQ, FIB, MATCHING, etc.
    difficulty: str = Field(..., min_length=1)  # easy, medium, hard
    explanation: Optional[str] = Field(None, max_length=5000)
    time_limit: Optional[int] = Field(None, ge=0)
    audio_url: Optional[str] = Field(None, max_length=500)
    image_url: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None
    source: Optional[str] = Field(None, max_length=255)


class QuestionCreate(QuestionBase):
    """Create question schema."""
    answers: List[AnswerCreate]


class QuestionResponse(QuestionBase):
    """Question response schema."""
    id: UUID
    answers: List[AnswerResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PublicAnswerResponse(BaseModel):
    """Answer option without correctness metadata for active practice."""
    id: UUID
    text: str
    order: int

    class Config:
        from_attributes = True


class QuestionPracticeResponse(BaseModel):
    """Question payload that does not reveal the answer key or explanation."""
    id: UUID
    text: str
    exam_type: str
    section: str
    question_type: str
    difficulty: str
    answers: List[PublicAnswerResponse]

    class Config:
        from_attributes = True


class QuestionListResponse(BaseModel):
    """Simplified question response for lists."""
    id: UUID
    text: str
    exam_type: str
    section: str
    question_type: str
    difficulty: str


# ============================================================================
# User Answer Schemas
# ============================================================================

class UserAnswerCreate(BaseModel):
    """Submit answer schema."""
    question_id: UUID
    answer_id: Optional[UUID] = None  # For MCQ/matching
    user_text_answer: Optional[str] = None  # For essay/short answer
    time_taken: Optional[int] = Field(None, ge=0)
    session_id: Optional[UUID] = None


class UserAnswerResponse(BaseModel):
    """User answer response schema."""
    id: UUID
    user_id: UUID
    question_id: UUID
    answer_id: Optional[UUID]
    user_text_answer: Optional[str]
    is_correct: Optional[bool]
    time_taken: Optional[int]
    attempts: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PracticeAnswerResult(BaseModel):
    """Grading feedback returned only after a learner submits an answer."""
    id: UUID
    question_id: UUID
    is_correct: Optional[bool]
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    attempts: int


# ============================================================================
# Passage Schemas
# ============================================================================

class PassageBase(BaseModel):
    """Base passage schema."""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=100)
    word_count: int = Field(..., ge=0)
    exam_type: str
    difficulty: str  # easy, medium, hard
    topic: Optional[str] = Field(None, max_length=255)
    source: Optional[str] = Field(None, max_length=255)
    time_limit: int = Field(..., ge=60)  # seconds


class PassageCreate(PassageBase):
    """Create passage schema."""
    pass


class PassageResponse(PassageBase):
    """Passage response schema."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PassageWithQuestionsResponse(PassageResponse):
    """Passage with related questions."""
    questions: List[QuestionPracticeResponse] = []


# ============================================================================
# Listening Track Schemas
# ============================================================================

class ListeningTrackBase(BaseModel):
    """Base listening track schema."""
    title: str = Field(..., min_length=1, max_length=255)
    audio_url: str = Field(..., max_length=500)
    duration: int = Field(..., ge=0)
    transcript: Optional[str] = None
    exam_type: str
    difficulty: str
    topic: Optional[str] = Field(None, max_length=255)
    source: Optional[str] = Field(None, max_length=255)
    accent: Optional[str] = Field(None, max_length=50)
    play_count: int = Field(1, ge=1)


class ListeningTrackCreate(ListeningTrackBase):
    """Create listening track schema."""
    pass


class ListeningTrackResponse(ListeningTrackBase):
    """Listening track response schema."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ListeningTrackWithQuestionsResponse(ListeningTrackResponse):
    """Listening track with only its linked public practice questions."""
    questions: List[QuestionPracticeResponse] = []


# ============================================================================
# Vocabulary Schemas
# ============================================================================

class VocabularyWordBase(BaseModel):
    """Base vocabulary word schema."""
    word: str = Field(..., min_length=1, max_length=255)
    definition: str = Field(..., min_length=1, max_length=2000)
    part_of_speech: str = Field(..., min_length=1, max_length=50)
    pronunciation: Optional[str] = Field(None, max_length=255)
    examples: Optional[List[str]] = None
    synonyms: Optional[List[str]] = None
    antonyms: Optional[List[str]] = None
    exam_type: str
    difficulty: str
    frequency: int = Field(0, ge=0)
    source: Optional[str] = Field(None, max_length=255)


class VocabularyWordCreate(VocabularyWordBase):
    """Create vocabulary word schema."""
    pass


class VocabularyWordResponse(VocabularyWordBase):
    """Vocabulary word response schema."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserVocabularyUpdate(BaseModel):
    """Update user vocabulary schema."""
    proficiency_level: int = Field(..., ge=1, le=5)


class UserVocabularyResponse(BaseModel):
    """User vocabulary response schema."""
    id: UUID
    word_id: UUID
    word: VocabularyWordResponse
    proficiency_level: int
    review_count: int
    last_reviewed: Optional[datetime]
    next_review: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Grammar Schemas
# ============================================================================

class GrammarExerciseBase(BaseModel):
    """Base grammar exercise schema."""
    sentence: str = Field(..., min_length=1, max_length=1000)
    correct_form: str = Field(..., min_length=1, max_length=500)
    explanation: Optional[str] = Field(None, max_length=2000)
    difficulty: str  # easy, medium, hard
    hint: Optional[str] = Field(None, max_length=500)


class GrammarExerciseCreate(GrammarExerciseBase):
    """Create grammar exercise schema."""
    topic_id: UUID


class GrammarExerciseResponse(GrammarExerciseBase):
    """Grammar exercise response schema."""
    id: UUID
    topic_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class GrammarExercisePracticeResponse(BaseModel):
    """Public exercise fields without the solution or explanation."""
    id: UUID
    topic_id: UUID
    sentence: str
    difficulty: str
    hint: Optional[str]

    class Config:
        from_attributes = True


class GrammarTopicBase(BaseModel):
    """Base grammar topic schema."""
    topic_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    explanation: Optional[str] = None
    examples: Optional[List[str]] = None
    exam_type: str
    difficulty: str
    order: int = Field(0, ge=0)


class GrammarTopicCreate(GrammarTopicBase):
    """Create grammar topic schema."""
    pass


class GrammarTopicResponse(GrammarTopicBase):
    """Grammar topic response schema."""
    id: UUID
    exercises: List[GrammarExerciseResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GrammarTopicPracticeResponse(GrammarTopicBase):
    """Grammar topic with answer-key-safe exercise payloads."""
    id: UUID
    exercises: List[GrammarExercisePracticeResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GrammarExerciseAnswerSubmit(BaseModel):
    """Submit grammar exercise answer."""
    exercise_id: UUID
    user_answer: str = Field(..., min_length=1, max_length=500)


class GrammarAnswerResult(BaseModel):
    id: UUID
    exercise_id: UUID
    is_correct: bool
    correct_form: str
    explanation: Optional[str] = None
    attempt_number: int
    created_at: datetime


class GrammarAttemptHistoryItem(BaseModel):
    id: UUID
    exercise_id: UUID
    topic_name: str
    sentence: str
    user_answer: str
    is_correct: bool
    created_at: datetime


# ============================================================================
# Study Session & Progress Schemas
# ============================================================================

class StudySessionCreate(BaseModel):
    """Create study session schema."""
    exam_id: Optional[UUID] = None
    section: str
    duration: int = Field(..., ge=0)
    questions_attempted: int = Field(0, ge=0)
    questions_correct: int = Field(0, ge=0)
    notes: Optional[str] = None


class StudySessionComplete(BaseModel):
    session_id: UUID
    section: str
    duration: int = Field(..., ge=0)


class StudySessionResponse(BaseModel):
    """Study session response schema."""
    id: UUID
    user_id: UUID
    exam_id: Optional[UUID]
    session_id: Optional[UUID] = None
    section: str
    session_date: datetime
    duration: int
    questions_attempted: int
    questions_correct: int
    accuracy: Optional[float]
    score: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProgressResponse(BaseModel):
    """User progress response schema."""
    id: UUID
    user_id: UUID
    exam_id: UUID
    section: str
    total_questions: int
    correct_answers: int
    accuracy: Optional[float]
    average_score: Optional[float]
    last_practiced: Optional[datetime]
    study_streak: int
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProgressSummary(BaseModel):
    """Progress summary across all sections."""
    exam_id: UUID
    overall_accuracy: float
    sections: Dict[str, Dict[str, Any]]  # section -> {accuracy, score, last_practiced}
    total_questions_answered: int
    study_streak: int
    last_practiced: Optional[datetime]


class StudyRecommendation(BaseModel):
    section: str
    title: str
    reason: str
    href: str
    accuracy_percent: Optional[int] = None


class AchievementResponse(BaseModel):
    id: str
    title: str
    description: str
    current: int
    target: int
    unlocked: bool


# ============================================================================
# Query Schemas
# ============================================================================

class QuestionFilter(BaseModel):
    """Question filter schema."""
    exam_type: Optional[str] = None
    section: Optional[str] = None
    question_type: Optional[str] = None
    difficulty: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)


class PracticeSessionFilter(BaseModel):
    """Practice session filter schema."""
    exam_id: Optional[UUID] = None
    section: Optional[str] = None
    difficulty: Optional[str] = None
    limit: int = Field(10, ge=1, le=50)
