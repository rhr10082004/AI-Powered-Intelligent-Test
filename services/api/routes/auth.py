"""
Authentication API routes.
"""

import asyncio
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.config import get_settings
from services.api.database import get_db_session
from services.api.email import send_transactional_email
from services.api.models import AuthActionToken, User
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
RATE_WINDOW = timedelta(minutes=1)


class EmailActionRequest(BaseModel):
    email: EmailStr


class TokenActionRequest(BaseModel):
    token: str = Field(min_length=20, max_length=200)


class PasswordResetRequest(TokenActionRequest):
    password: str = Field(min_length=8, max_length=128)


async def _issue_action_token(
    session: AsyncSession,
    user: User,
    *,
    purpose: str,
    lifetime: timedelta,
) -> str | None:
    """Issue, persist and email a one-use token; throttle each account to one/minute."""
    now = datetime.utcnow()
    active = await session.execute(
        select(AuthActionToken).where(
            and_(
                AuthActionToken.user_id == user.id,
                AuthActionToken.purpose == purpose,
                AuthActionToken.used_at.is_(None),
                AuthActionToken.created_at > now - RATE_WINDOW,
            )
        )
    )
    if active.scalar_one_or_none():
        return None

    previous = await session.execute(
        select(AuthActionToken).where(
            and_(AuthActionToken.user_id == user.id,
                 AuthActionToken.purpose == purpose,
                 AuthActionToken.used_at.is_(None))
        )
    )
    for token_record in previous.scalars().all():
        token_record.used_at = now

    raw_token = secrets.token_urlsafe(32)
    session.add(AuthActionToken(
        user_id=user.id,
        purpose=purpose,
        token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
        expires_at=now + lifetime,
        created_at=now,
    ))
    await session.commit()

    settings = get_settings()
    path = "auth/verify-email" if purpose == "verify_email" else "auth/reset-password"
    action = "Verify your email" if purpose == "verify_email" else "Reset your password"
    link = f"{settings.frontend_url.rstrip('/')}/{path}?token={raw_token}"
    body = f"{action}\n\nUse this one-time link within {int(lifetime.total_seconds() // 60)} minutes:\n{link}\n\nIf you did not request this, you can ignore this email."
    try:
        sent = await asyncio.to_thread(
            send_transactional_email,
            settings,
            recipient=user.email,
            subject=f"Studywell: {action}",
            body=body,
        )
    except (OSError, TimeoutError, Exception):
        # Keep account-existence responses generic; failed delivery is not exposed.
        sent = False
    if not sent and settings.environment.casefold() != "production":
        return raw_token
    return None


async def _consume_action_token(
    session: AsyncSession, raw_token: str, purpose: str
) -> tuple[AuthActionToken, User] | None:
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    result = await session.execute(
        select(AuthActionToken, User)
        .join(User, User.id == AuthActionToken.user_id)
        .where(and_(AuthActionToken.token_hash == token_hash,
                    AuthActionToken.purpose == purpose,
                    AuthActionToken.used_at.is_(None),
                    AuthActionToken.expires_at > datetime.utcnow()))
    )
    return result.one_or_none()


@router.post("/email-verification/request")
async def request_email_verification(
    payload: EmailActionRequest,
    session: AsyncSessionDep,
) -> dict:
    """Send a verification link without disclosing whether the email exists."""
    user = await session.scalar(select(User).where(User.email == payload.email))
    debug_token = None
    if user and not user.is_verified and user.is_active:
        debug_token = await _issue_action_token(
            session, user, purpose="verify_email", lifetime=timedelta(hours=24)
        )
    response = {"message": "If the account can be verified, a link will be sent shortly."}
    if debug_token:
        response["debug_token"] = debug_token
    return response


@router.post("/email-verification/confirm", response_model=MessageResponse)
async def confirm_email_verification(
    payload: TokenActionRequest,
    session: AsyncSessionDep,
) -> MessageResponse:
    match = await _consume_action_token(session, payload.token, "verify_email")
    if not match:
        raise HTTPException(status_code=400, detail="This verification link is invalid or expired.")
    token_record, user = match
    token_record.used_at = datetime.utcnow()
    user.is_verified = True
    await session.commit()
    return MessageResponse(message="Email address verified. You can now sign in.")


@router.post("/password-reset/request")
async def request_password_reset(
    payload: EmailActionRequest,
    session: AsyncSessionDep,
) -> dict:
    """Send a password reset link with a generic account-existence response."""
    user = await session.scalar(select(User).where(User.email == payload.email))
    debug_token = None
    if user and user.is_active:
        debug_token = await _issue_action_token(
            session, user, purpose="password_reset", lifetime=timedelta(minutes=30)
        )
    response = {"message": "If that account exists, a reset link will be sent shortly."}
    if debug_token:
        response["debug_token"] = debug_token
    return response


@router.post("/password-reset/confirm", response_model=MessageResponse)
async def confirm_password_reset(
    payload: PasswordResetRequest,
    session: AsyncSessionDep,
) -> MessageResponse:
    match = await _consume_action_token(session, payload.token, "password_reset")
    if not match:
        raise HTTPException(status_code=400, detail="This reset link is invalid or expired.")
    token_record, user = match
    token_record.used_at = datetime.utcnow()
    user.hashed_password = hash_password(payload.password)
    await session.commit()
    return MessageResponse(message="Password updated. Sign in with your new password.")


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
