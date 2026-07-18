"""
Pydantic schemas for request/response validation.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from services.api.models import ExamType


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """User login schema."""

    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """User update schema."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


class UserResponse(UserBase):
    """User response schema."""

    id: UUID
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserSettingsBase(BaseModel):
    """Base user settings schema."""

    theme: str = Field("light", pattern="^(light|dark|auto)$")
    language: str = Field("en", min_length=2, max_length=10)
    notifications_email: bool = True
    notifications_push: bool = True
    notifications_reminder: bool = True


class UserSettingsUpdate(UserSettingsBase):
    """User settings update schema."""

    pass


class UserSettingsResponse(UserSettingsBase):
    """User settings response schema."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserExamCreate(BaseModel):
    """User exam creation schema."""

    exam_type: ExamType
    target_score: Optional[str] = None
    skill_level: str = Field("beginner", pattern="^(beginner|intermediate|advanced)$")


class UserExamUpdate(BaseModel):
    """User exam update schema."""

    target_score: Optional[str] = None
    skill_level: Optional[str] = None
    is_active: Optional[bool] = None


class UserExamResponse(BaseModel):
    """User exam response schema."""

    id: UUID
    user_id: UUID
    exam_type: ExamType
    target_score: Optional[str] = None
    skill_level: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    """JWT token payload schema."""

    sub: str  # user_id
    iat: int  # issued at
    exp: int  # expiration
    type: str = "access"  # access or refresh


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
    code: Optional[str] = None
    details: Optional[dict] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: datetime
    version: str
    environment: str


class PaginationParams(BaseModel):
    """Pagination parameters."""

    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""

    total: int
    skip: int
    limit: int
    items: list
