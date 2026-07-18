"""
User profile API routes.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.database import get_db_session
from services.api.models import User
from services.api.schemas import MessageResponse, UserResponse, UserUpdate
from services.api.utils.auth import verify_token

router = APIRouter(prefix="/users", tags=["users"])

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


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    token: str,
    session: AsyncSessionDep,
) -> UserResponse:
    """
    Get current user profile.
    
    - **token**: JWT access token (can be in Authorization header)
    """
    user = await get_current_user(token, session)
    return UserResponse.model_validate(user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    token: str,
    user_update: UserUpdate,
    session: AsyncSessionDep,
) -> UserResponse:
    """
    Update current user profile.
    
    - **token**: JWT access token
    - **first_name**: Optional first name
    - **last_name**: Optional last name
    - **avatar_url**: Optional avatar URL
    - **bio**: Optional biography
    """
    user = await get_current_user(token, session)
    
    # Update only provided fields
    if user_update.first_name is not None:
        user.first_name = user_update.first_name
    if user_update.last_name is not None:
        user.last_name = user_update.last_name
    if user_update.avatar_url is not None:
        user.avatar_url = user_update.avatar_url
    if user_update.bio is not None:
        user.bio = user_update.bio
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    session: AsyncSessionDep,
) -> UserResponse:
    """
    Get user profile by ID.
    
    - **user_id**: UUID of the user
    """
    stmt = select(User).where(User.id == user_id)
    user = await session.execute(stmt)
    user_obj = user.scalar_one_or_none()
    
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse.model_validate(user_obj)


@router.delete("/me", response_model=MessageResponse)
async def delete_current_user(
    token: str,
    session: AsyncSessionDep,
) -> MessageResponse:
    """
    Soft delete current user account.
    
    - **token**: JWT access token
    """
    user = await get_current_user(token, session)
    
    # Soft delete
    user.is_deleted = True
    user.is_active = False
    
    session.add(user)
    await session.commit()
    
    return MessageResponse(message="User account deleted successfully")
