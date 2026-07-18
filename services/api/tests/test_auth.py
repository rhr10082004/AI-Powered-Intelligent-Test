"""Test authentication utilities."""

import pytest
from services.api.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
)
from uuid import uuid4


def test_hash_password():
    """Test password hashing."""
    password = "test_password_123"
    hashed = hash_password(password)
    
    # Hash should not be the same as password
    assert hashed != password
    # Hash should be long (bcrypt)
    assert len(hashed) > 50


def test_verify_password():
    """Test password verification."""
    password = "test_password_123"
    hashed = hash_password(password)
    
    # Correct password should verify
    assert verify_password(password, hashed) is True
    
    # Wrong password should not verify
    assert verify_password("wrong_password", hashed) is False


def test_create_access_token():
    """Test access token creation."""
    user_id = uuid4()
    token = create_access_token(user_id)
    
    # Token should be a string
    assert isinstance(token, str)
    
    # Token should have three parts (JWT format)
    assert len(token.split('.')) == 3


def test_verify_token():
    """Test token verification."""
    user_id = uuid4()
    token = create_access_token(user_id)
    
    # Verify token should return the user_id
    verified_user_id = verify_token(token, token_type="access")
    assert verified_user_id == user_id


def test_verify_invalid_token():
    """Test verification of invalid token."""
    # Invalid token should return None
    result = verify_token("invalid.token.here", token_type="access")
    assert result is None


def test_verify_wrong_token_type():
    """Test verification with wrong token type."""
    user_id = uuid4()
    token = create_access_token(user_id)
    
    # Verify as refresh token (wrong type) should return None
    result = verify_token(token, token_type="refresh")
    assert result is None
