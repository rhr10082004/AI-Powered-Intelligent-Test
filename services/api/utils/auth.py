"""
Authentication utilities for JWT and password management.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import jwt
from passlib.context import CryptContext

from services.api.config import get_settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: UUID, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    settings = get_settings()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            hours=settings.jwt_expiration_hours
        )
    
    to_encode = {
        "sub": str(user_id),
        "iat": datetime.now(timezone.utc),
        "exp": expire,
        "type": "access",
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    
    return encoded_jwt


def create_refresh_token(user_id: UUID) -> str:
    """Create JWT refresh token."""
    settings = get_settings()
    
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expiration_days
    )
    
    to_encode = {
        "sub": str(user_id),
        "iat": datetime.now(timezone.utc),
        "exp": expire,
        "type": "refresh",
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and validate JWT token."""
    settings = get_settings()
    
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except jwt.InvalidTokenError:
        return {}


def verify_token(token: str, token_type: str = "access") -> Optional[UUID]:
    """Verify token and return user_id if valid."""
    payload = decode_token(token)
    
    if not payload:
        return None
    
    # Check token type
    if payload.get("type") != token_type:
        return None
    
    # Check expiration (jwt.decode will raise if expired, but double-check)
    exp = payload.get("exp")
    if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
        return None
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        return None
    
    try:
        return UUID(user_id_str)
    except ValueError:
        return None
