"""
SQLAlchemy ORM models for the application.
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    TypeDecorator,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from services.api.database import Base


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


class ExamType(str, Enum):
    """Available exam types."""

    IELTS = "ielts"
    GRE = "gre"
    TOEFL = "toefl"


class Difficulty(str, Enum):
    """Question difficulty."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Section(str, Enum):
    """Practice section."""

    READING = "reading"
    LISTENING = "listening"


class QuestionType(str, Enum):
    """Supported question types."""

    MCQ = "mcq"
    FIB = "fib"
    MATCHING = "matching"
    ESSAY = "essay"
    SPEAKING = "speaking"


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class AuthActionToken(Base):
    """Hashed, one-use email verification and password reset token."""

    __tablename__ = "auth_action_tokens"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    purpose = Column(String(32), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class UserSettings(Base):
    """User preferences and settings."""

    __tablename__ = "user_settings"

    id = Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_id = Column(GUID(), nullable=False, unique=True, index=True)
    theme = Column(String(20), default="light", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    notifications_email = Column(Boolean, default=True, nullable=False)
    notifications_push = Column(Boolean, default=True, nullable=False)
    notifications_reminder = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<UserSettings(user_id={self.user_id})>"


class UserExam(Base):
    """User enrollment in exams."""

    __tablename__ = "user_exams"

    id = Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_id = Column(GUID(), nullable=False, index=True)
    exam_type = Column(SQLEnum(ExamType), nullable=False)
    target_score = Column(String(20), nullable=True)
    skill_level = Column(String(20), default="beginner", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "exam_type", name="uq_user_exams_user_exam"),
    )

    def __repr__(self) -> str:
        return f"<UserExam(user_id={self.user_id}, exam_type={self.exam_type})>"


class AuditLog(Base):
    """Audit log for tracking changes."""

    __tablename__ = "audit_logs"

    id = Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_id = Column(GUID(), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(GUID(), nullable=True)
    description = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<AuditLog(action={self.action}, entity_type={self.entity_type})>"


class Passage(Base):
    """Reading passage content."""

    __tablename__ = "passages"

    id = Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    exam_type = Column(SQLEnum(ExamType), nullable=False)
    difficulty = Column(SQLEnum(Difficulty), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class Question(Base):
    """Question bank item."""

    __tablename__ = "questions"

    id = Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    text = Column(Text, nullable=False)
    exam_type = Column(SQLEnum(ExamType), nullable=False)
    section = Column(SQLEnum(Section), nullable=False)
    difficulty = Column(SQLEnum(Difficulty), nullable=False)
    question_type = Column(SQLEnum(QuestionType), nullable=False)
    passage_id = Column(GUID(), ForeignKey("passages.id"), nullable=True)
    explanation = Column(Text, nullable=True)
    audio_url = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    passage = relationship("Passage", backref="questions")


class Answer(Base):
    """Answer option for a question."""

    __tablename__ = "answers"

    id = Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    question_id = Column(GUID(), ForeignKey("questions.id"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    question = relationship("Question", backref="answers")


class UserAnswer(Base):
    """Tracking attempts for a user answering a question."""

    __tablename__ = "user_answers"

    id = Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(GUID(), ForeignKey("questions.id"), nullable=False, index=True)
    selected_answer_id = Column(GUID(), ForeignKey("answers.id"), nullable=True)
    is_correct = Column(Boolean, default=False, nullable=False)
    time_taken = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User", backref="answers_attempts")
    question = relationship("Question", backref="user_answers")
    selected_answer = relationship("Answer")
