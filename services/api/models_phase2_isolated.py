"""Phase 2 isolated SQLAlchemy models for learning content.

This file intentionally uses its own declarative Base to prevent table
mapping collisions with Phase 1 models.

Fixes runtime error:
  Table 'questions' is already defined for this MetaData instance
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    Table,
    TypeDecorator,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship


BasePhase2 = declarative_base()


class GUID(TypeDecorator):
    """SQLite/Postgres-compatible UUID column type."""

    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return uuid.UUID(value)


passage_questions = Table(
    "learning_passage_questions",
    BasePhase2.metadata,
    Column("passage_id", GUID(), ForeignKey("learning_passages.id"), primary_key=True),
    Column("question_id", GUID(), ForeignKey("learning_questions.id"), primary_key=True),
)

listening_questions = Table(
    "learning_listening_questions",
    BasePhase2.metadata,
    Column("track_id", GUID(), ForeignKey("learning_listening_tracks.id"), primary_key=True),
    Column("question_id", GUID(), ForeignKey("learning_questions.id"), primary_key=True),
)


class QuestionTypeEnum(str, PyEnum):
    """Question type enumeration."""

    MCQ = "MCQ"  # Multiple Choice Questions
    FIB = "FIB"  # Fill in the Blank
    MATCHING = "MATCHING"
    ESSAY = "ESSAY"
    SPEAKING = "SPEAKING"
    SHORT_ANSWER = "SHORT_ANSWER"


class DifficultyEnum(str, PyEnum):
    """Difficulty level enumeration."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class SectionEnum(str, PyEnum):
    """Exam section enumeration."""

    READING = "reading"
    LISTENING = "listening"
    WRITING = "writing"
    SPEAKING = "speaking"
    VOCABULARY = "vocabulary"
    GRAMMAR = "grammar"


class ExamTypeEnum(str, PyEnum):
    """Supported exam types."""

    IELTS = "IELTS"
    GRE = "GRE"
    TOEFL = "TOEFL"


class Question(BasePhase2):
    """Question model for all exam questions."""

    __tablename__ = "learning_questions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    text = Column(Text, nullable=False)
    exam_type = Column(String(50), nullable=False)  # IELTS, GRE, TOEFL
    section = Column(String(50), nullable=False)  # reading, listening, writing, speaking
    subsection = Column(String(100), nullable=True)
    question_type = Column(String(50), nullable=False)
    difficulty = Column(String(50), nullable=False)

    explanation = Column(Text, nullable=True)
    time_limit = Column(Integer, nullable=True)

    audio_url = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)

    tags = Column(JSON, nullable=True)
    source = Column(String(255), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    user_answers = relationship(
        "UserAnswer", back_populates="question", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("exam_type", "section", "text", name="uq_question_unique"),
    )


class Answer(BasePhase2):
    """Answer options for questions."""

    __tablename__ = "learning_answers"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    question_id = Column(GUID(), ForeignKey("learning_questions.id"), nullable=False)
    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    explanation = Column(Text, nullable=True)
    order = Column(Integer, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    question = relationship("Question", back_populates="answers")
    user_answers = relationship("UserAnswer", back_populates="answer")


class UserAnswer(BasePhase2):
    """Track user's answers to questions."""

    __tablename__ = "learning_user_answers"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False)
    question_id = Column(GUID(), ForeignKey("learning_questions.id"), nullable=False)
    answer_id = Column(GUID(), ForeignKey("learning_answers.id"), nullable=True)

    user_text_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    time_taken = Column(Integer, nullable=True)
    attempts = Column(Integer, nullable=False, default=1)
    review_count = Column(Integer, nullable=False, default=0)
    session_id = Column(GUID(), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    question = relationship("Question", back_populates="user_answers")
    answer = relationship("Answer", back_populates="user_answers")


class Passage(BasePhase2):
    """Reading passages for reading section."""

    __tablename__ = "learning_passages"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=False)
    exam_type = Column(String(50), nullable=False)
    difficulty = Column(String(50), nullable=False)
    topic = Column(String(255), nullable=True)
    source = Column(String(255), nullable=True)
    time_limit = Column(Integer, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    questions = relationship("Question", secondary=passage_questions, viewonly=True)


class ListeningTrack(BasePhase2):
    """Audio tracks for listening section."""

    __tablename__ = "learning_listening_tracks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    audio_url = Column(String(500), nullable=False)
    duration = Column(Integer, nullable=False)
    transcript = Column(Text, nullable=True)

    exam_type = Column(String(50), nullable=False)
    difficulty = Column(String(50), nullable=False)
    topic = Column(String(255), nullable=True)
    source = Column(String(255), nullable=True)
    accent = Column(String(50), nullable=True)
    play_count = Column(Integer, nullable=False, default=1)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    questions = relationship("Question", secondary=listening_questions, viewonly=True)


class VocabularyWord(BasePhase2):
    """Vocabulary words for learning."""

    __tablename__ = "learning_vocabulary_words"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    word = Column(String(255), nullable=False, unique=True)
    definition = Column(Text, nullable=False)
    part_of_speech = Column(String(50), nullable=False)
    pronunciation = Column(String(255), nullable=True)

    examples = Column(JSON, nullable=True)
    synonyms = Column(JSON, nullable=True)
    antonyms = Column(JSON, nullable=True)

    exam_type = Column(String(50), nullable=False)
    difficulty = Column(String(50), nullable=False)
    frequency = Column(Integer, nullable=False, default=0)
    source = Column(String(255), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_vocabulary = relationship(
        "UserVocabulary", back_populates="word", cascade="all, delete-orphan"
    )


class UserVocabulary(BasePhase2):
    """Track user's vocabulary learning progress."""

    __tablename__ = "learning_user_vocabulary"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False)
    word_id = Column(GUID(), ForeignKey("learning_vocabulary_words.id"), nullable=False)

    proficiency_level = Column(Integer, nullable=False, default=1)
    review_count = Column(Integer, nullable=False, default=0)
    last_reviewed = Column(DateTime, nullable=True)
    next_review = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    word = relationship("VocabularyWord", back_populates="user_vocabulary")


class GrammarTopic(BasePhase2):
    """Grammar topics for organized learning."""

    __tablename__ = "learning_grammar_topics"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    topic_name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    examples = Column(JSON, nullable=True)

    exam_type = Column(String(50), nullable=False)
    difficulty = Column(String(50), nullable=False)
    order = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    exercises = relationship(
        "GrammarExercise", back_populates="topic", cascade="all, delete-orphan"
    )


class GrammarExercise(BasePhase2):
    """Grammar exercises under topics."""

    __tablename__ = "learning_grammar_exercises"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    topic_id = Column(GUID(), ForeignKey("learning_grammar_topics.id"), nullable=False)
    sentence = Column(Text, nullable=False)
    correct_form = Column(String(500), nullable=False)
    explanation = Column(Text, nullable=True)
    difficulty = Column(String(50), nullable=False)
    hint = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    topic = relationship("GrammarTopic", back_populates="exercises")


class GrammarAttempt(BasePhase2):
    """A private, durable answer attempt for a grammar exercise."""

    __tablename__ = "learning_grammar_attempts"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False, index=True)
    exercise_id = Column(
        GUID(), ForeignKey("learning_grammar_exercises.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_answer = Column(String(500), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


class StudySession(BasePhase2):
    """Track user's study sessions."""

    __tablename__ = "learning_study_sessions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False)
    exam_id = Column(GUID(), nullable=True)
    session_id = Column(GUID(), nullable=True)

    section = Column(String(50), nullable=False)
    session_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    duration = Column(Integer, nullable=False)
    questions_attempted = Column(Integer, nullable=False, default=0)
    questions_correct = Column(Integer, nullable=False, default=0)
    accuracy = Column(Float, nullable=True)
    score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "exam_id", "session_date", name="uq_study_session"),
        UniqueConstraint("user_id", "session_id", name="uq_study_session_user_session"),
    )


class UserProgress(BasePhase2):
    """Track user's overall progress."""

    __tablename__ = "learning_user_progress"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False)
    exam_id = Column(GUID(), nullable=False)

    section = Column(String(50), nullable=False)
    total_questions = Column(Integer, nullable=False, default=0)
    correct_answers = Column(Integer, nullable=False, default=0)
    accuracy = Column(Float, nullable=True)
    average_score = Column(Float, nullable=True)
    last_practiced = Column(DateTime, nullable=True)
    study_streak = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "exam_id", "section", name="uq_progress_user_exam_section"),
    )


class TutorConversation(BasePhase2):
    """A private, persistent tutor conversation owned by one user."""

    __tablename__ = "learning_tutor_conversations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    exam_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship(
        "TutorMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="TutorMessage.created_at",
    )


class TutorMessage(BasePhase2):
    """One learner or tutor turn in a persisted conversation."""

    __tablename__ = "learning_tutor_messages"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        GUID(),
        ForeignKey("learning_tutor_conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    conversation = relationship("TutorConversation", back_populates="messages")

class WritingSubmission(BasePhase2):
    """Saved writing practice with private, criterion-level feedback."""

    __tablename__ = "learning_writing_submissions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False, index=True)
    exam_type = Column(String(50), nullable=False)
    prompt = Column(Text, nullable=False)
    essay = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=False)
    estimated_band = Column(Float, nullable=False)
    evaluation_method = Column(String(20), nullable=False)
    feedback = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


class SpeakingSubmission(BasePhase2):
    """Private speaking transcript practice with transcript-only feedback."""

    __tablename__ = "learning_speaking_submissions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False, index=True)
    exam_type = Column(String(50), nullable=False)
    prompt = Column(Text, nullable=False)
    transcript = Column(Text, nullable=False)
    estimated_score = Column(Float, nullable=False)
    feedback = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


class MockTestAttempt(BasePhase2):
    """Private adaptive reading/listening mock test and its saved results."""

    __tablename__ = "learning_mock_test_attempts"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False, index=True)
    exam_type = Column(String(50), nullable=False)
    question_ids = Column(JSON, nullable=False)
    adaptive_level = Column(String(30), nullable=False)
    responses = Column(JSON, nullable=False, default=dict)
    section_scores = Column(JSON, nullable=False, default=dict)
    topic_scores = Column(JSON, nullable=False, default=dict)
    question_count = Column(Integer, nullable=False)
    correct_count = Column(Integer, nullable=False, default=0)
    accuracy = Column(Float, nullable=True)
    completed_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


class DailyStudyPlan(BasePhase2):
    """One generated, learner-owned study plan per exam and calendar day."""

    __tablename__ = "learning_daily_study_plans"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False, index=True)
    exam_type = Column(String(50), nullable=False, default="GENERAL")
    plan_date = Column(DateTime, nullable=False, index=True)
    target_minutes = Column(Integer, nullable=False, default=30)
    tasks = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "exam_type", "plan_date", name="uq_daily_plan_user_exam_date"),
    )


class ActivityEvent(BasePhase2):
    """Append-only learner activity and points ledger."""

    __tablename__ = "learning_activity_events"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=False, index=True)
    event_key = Column(String(160), nullable=False)
    event_type = Column(String(50), nullable=False, index=True)
    section = Column(String(50), nullable=True)
    reference_id = Column(GUID(), nullable=True)
    details = Column(JSON, nullable=False, default=dict)
    points = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    __table_args__ = (
        UniqueConstraint("user_id", "event_key", name="uq_activity_user_event_key"),
    )
