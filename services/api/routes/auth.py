"""
Authentication API routes.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.database import get_db_session
from services.api.models import User
from services.api.schemas import (
    MessageResponse,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from services.api.utils.auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])

AsyncSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, session: AsyncSessionDep) -> TokenResponse:
    """
    Register a new user.
    
    - **email**: User email address (must be unique)
    - **password**: Password (minimum 8 characters)
    - **first_name**: Optional first name
    - **last_name**: Optional last name
    """
    # Check if user already exists
    stmt = select(User).where(User.email == user_data.email)
    existing_user = await session.execute(stmt)
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        is_verified=False,
    )
    
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    # Create tokens
    access_token = create_access_token(new_user.id)
    refresh_token = create_refresh_token(new_user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=3600,  # 1 hour in seconds
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, session: AsyncSessionDep) -> TokenResponse:
    """
    Login user with email and password.
    
    - **email**: User email address
    - **password**: User password
    """
    # Find user by email
    stmt = select(User).where(User.email == credentials.email)
    user = await session.execute(stmt)
    user_obj = user.scalar_one_or_none()
    
    if not user_obj or not verify_password(credentials.password, user_obj.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    if not user_obj.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )
    
    # Create tokens
    access_token = create_access_token(user_obj.id)
    refresh_token = create_refresh_token(user_obj.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=3600,
    )


@router.post("/verify-token", response_model=UserResponse)
async def verify_token_endpoint(
    token: str,
    session: AsyncSessionDep,
) -> UserResponse:
    """
    Verify JWT token and return user info.
    
    - **token**: JWT access token
    """
    user_id = verify_token(token, token_type="access")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    # Fetch user from database
    stmt = select(User).where(User.id == user_id)
    user = await session.execute(stmt)
    user_obj = user.scalar_one_or_none()
    
    if not user_obj or not user_obj.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    return UserResponse.model_validate(user_obj)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_token: str,
) -> TokenResponse:
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: JWT refresh token
    """
    user_id = verify_token(refresh_token, token_type="refresh")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    # Create new access token
    access_token = create_access_token(user_id)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=3600,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout() -> MessageResponse:
    """
    Logout user (client-side token deletion).
    
    Note: Token blacklisting not implemented (stateless JWT).
    Client should delete tokens locally.
    """
    return MessageResponse(message="Logged out successfully")
