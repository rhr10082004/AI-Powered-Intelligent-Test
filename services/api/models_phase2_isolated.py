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
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship


BasePhase2 = declarative_base()


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

    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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

    __tablename__ = "answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    explanation = Column(Text, nullable=True)
    order = Column(Integer, nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    question = relationship("Question", back_populates="answers")
    user_answers = relationship("UserAnswer", back_populates="answer")


class UserAnswer(BasePhase2):
    """Track user's answers to questions."""

    __tablename__ = "user_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    answer_id = Column(UUID(as_uuid=True), ForeignKey("answers.id"), nullable=True)

    user_text_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    time_taken = Column(Integer, nullable=True)
    attempts = Column(Integer, nullable=False, default=1)
    review_count = Column(Integer, nullable=False, default=0)
    session_id = Column(UUID(as_uuid=True), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    question = relationship("Question", back_populates="user_answers")
    answer = relationship("Answer", back_populates="user_answers")


class Passage(BasePhase2):
    """Reading passages for reading section."""

    __tablename__ = "passages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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

    questions = relationship("Question", secondary="passage_questions", viewonly=True)


class ListeningTrack(BasePhase2):
    """Audio tracks for listening section."""

    __tablename__ = "listening_tracks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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


class VocabularyWord(BasePhase2):
    """Vocabulary words for learning."""

    __tablename__ = "vocabulary_words"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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

    __tablename__ = "user_vocabulary"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    word_id = Column(UUID(as_uuid=True), ForeignKey("vocabulary_words.id"), nullable=False)

    proficiency_level = Column(Integer, nullable=False, default=1)
    review_count = Column(Integer, nullable=False, default=0)
    last_reviewed = Column(DateTime, nullable=True)
    next_review = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    word = relationship("VocabularyWord", back_populates="user_vocabulary")


class GrammarTopic(BasePhase2):
    """Grammar topics for organized learning."""

    __tablename__ = "grammar_topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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

    __tablename__ = "grammar_exercises"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("grammar_topics.id"), nullable=False)
    sentence = Column(Text, nullable=False)
    correct_form = Column(String(500), nullable=False)
    explanation = Column(Text, nullable=True)
    difficulty = Column(String(50), nullable=False)
    hint = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    topic = relationship("GrammarTopic", back_populates="exercises")


class StudySession(BasePhase2):
    """Track user's study sessions."""

    __tablename__ = "study_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    exam_id = Column(UUID(as_uuid=True), ForeignKey("user_exams.id"), nullable=True)

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
    )


class UserProgress(BasePhase2):
    """Track user's overall progress."""

    __tablename__ = "user_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    exam_id = Column(UUID(as_uuid=True), ForeignKey("user_exams.id"), nullable=False)

    section = Column(String(50), nullable=False)
    total_questions = Column(Integer, nullable=False, default=0)
    correct_answers = Column(Integer, nullable=False, default=0)
    accuracy = Column(Float, nullable=True)
    average_score = Column(Float, nullable=True)
    last_practiced = Column(DateTime, nullable=True)
    study_streak = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

