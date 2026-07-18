"""
User exam enrollment API routes.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.database import get_db_session
from services.api.models import ExamType, User, UserExam
from services.api.schemas import (
    MessageResponse,
    UserExamCreate,
    UserExamResponse,
    UserExamUpdate,
)
from services.api.utils.auth import verify_token

router = APIRouter(prefix="/exams", tags=["exams"])

AsyncSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


async def get_current_user(
    token: str,
    session: AsyncSessionDep,
) -> User:
    """Dependency to get current authenticated user."""
    user_id = verify_token(token, token_type="access")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    stmt = select(User).where(User.id == user_id)
    user = await session.execute(stmt)
    user_obj = user.scalar_one_or_none()
    
    if not user_obj or not user_obj.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    return user_obj


@router.get("/my-exams", response_model=list[UserExamResponse])
async def get_my_exams(
    token: str,
    session: AsyncSessionDep,
) -> list[UserExamResponse]:
    """
    Get current user's enrolled exams.
    
    - **token**: JWT access token
    """
    user = await get_current_user(token, session)
    
    stmt = select(UserExam).where(UserExam.user_id == user.id)
    exams = await session.execute(stmt)
    exam_list = exams.scalars().all()
    
    return [UserExamResponse.model_validate(exam) for exam in exam_list]


@router.post("/enroll", response_model=UserExamResponse)
async def enroll_exam(
    token: str,
    exam_data: UserExamCreate,
    session: AsyncSessionDep,
) -> UserExamResponse:
    """
    Enroll user in an exam.
    
    - **token**: JWT access token
    - **exam_type**: IELTS, GRE, or TOEFL
    - **target_score**: Optional target score (e.g., "7.5" for IELTS)
    - **skill_level**: beginner, intermediate, or advanced
    """
    user = await get_current_user(token, session)
    
    # Check if user is already enrolled
    stmt = select(UserExam).where(
        (UserExam.user_id == user.id) & (UserExam.exam_type == exam_data.exam_type)
    )
    existing = await session.execute(stmt)
    
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User already enrolled in {exam_data.exam_type}",
        )
    
    # Create new exam enrollment
    new_exam = UserExam(
        user_id=user.id,
        exam_type=exam_data.exam_type,
        target_score=exam_data.target_score,
        skill_level=exam_data.skill_level,
    )
    
    session.add(new_exam)
    await session.commit()
    await session.refresh(new_exam)
    
    return UserExamResponse.model_validate(new_exam)


@router.get("/{exam_id}", response_model=UserExamResponse)
async def get_exam_by_id(
    token: str,
    exam_id: UUID,
    session: AsyncSessionDep,
) -> UserExamResponse:
    """
    Get exam details.
    
    - **token**: JWT access token
    - **exam_id**: UUID of the exam enrollment
    """
    user = await get_current_user(token, session)
    
    stmt = select(UserExam).where(
        (UserExam.id == exam_id) & (UserExam.user_id == user.id)
    )
    exam = await session.execute(stmt)
    exam_obj = exam.scalar_one_or_none()
    
    if not exam_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found",
        )
    
    return UserExamResponse.model_validate(exam_obj)


@router.put("/{exam_id}", response_model=UserExamResponse)
async def update_exam(
    token: str,
    exam_id: UUID,
    exam_update: UserExamUpdate,
    session: AsyncSessionDep,
) -> UserExamResponse:
    """
    Update exam enrollment details.
    
    - **token**: JWT access token
    - **exam_id**: UUID of the exam enrollment
    - **target_score**: Optional target score
    - **skill_level**: Optional skill level
    - **is_active**: Optional active status
    """
    user = await get_current_user(token, session)
    
    stmt = select(UserExam).where(
        (UserExam.id == exam_id) & (UserExam.user_id == user.id)
    )
    exam = await session.execute(stmt)
    exam_obj = exam.scalar_one_or_none()
    
    if not exam_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found",
        )
    
    # Update only provided fields
    if exam_update.target_score is not None:
        exam_obj.target_score = exam_update.target_score
    if exam_update.skill_level is not None:
        exam_obj.skill_level = exam_update.skill_level
    if exam_update.is_active is not None:
        exam_obj.is_active = exam_update.is_active
    
    session.add(exam_obj)
    await session.commit()
    await session.refresh(exam_obj)
    
    return UserExamResponse.model_validate(exam_obj)


@router.delete("/{exam_id}", response_model=MessageResponse)
async def unenroll_exam(
    token: str,
    exam_id: UUID,
    session: AsyncSessionDep,
) -> MessageResponse:
    """
    Unenroll user from an exam.
    
    - **token**: JWT access token
    - **exam_id**: UUID of the exam enrollment
    """
    user = await get_current_user(token, session)
    
    stmt = select(UserExam).where(
        (UserExam.id == exam_id) & (UserExam.user_id == user.id)
    )
    exam = await session.execute(stmt)
    exam_obj = exam.scalar_one_or_none()
    
    if not exam_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found",
        )
    
    await session.delete(exam_obj)
    await session.commit()
    
    return MessageResponse(message="Unenrolled from exam successfully")
