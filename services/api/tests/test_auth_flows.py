"""One-time email verification and password reset flows."""

from types import SimpleNamespace
from uuid import uuid4

import pytest

from services.api.models import User
from services.api.utils.auth import hash_password, verify_password


@pytest.mark.asyncio
async def test_verification_tokens_are_one_time_and_account_scoped(client, test_db_session, monkeypatch):
    monkeypatch.setattr(
        "services.api.routes.auth.get_settings",
        lambda: SimpleNamespace(environment="development", frontend_url="http://localhost:3000"),
    )
    user = User(email=f"verify-{uuid4()}@example.com", hashed_password=hash_password("initial-pass"))
    test_db_session.add(user)
    await test_db_session.commit()

    request = await client.post("/api/auth/email-verification/request", json={"email": user.email})
    assert request.status_code == 200
    token = request.json()["debug_token"]
    assert user.is_verified is False
    confirm = await client.post("/api/auth/email-verification/confirm", json={"token": token})
    assert confirm.status_code == 200
    await test_db_session.refresh(user)
    assert user.is_verified is True
    reused = await client.post("/api/auth/email-verification/confirm", json={"token": token})
    assert reused.status_code == 400

    unknown = await client.post(
        "/api/auth/email-verification/request", json={"email": f"missing-{uuid4()}@example.com"}
    )
    assert unknown.status_code == 200
    assert "debug_token" not in unknown.json()


@pytest.mark.asyncio
async def test_password_reset_changes_password_and_consumes_token(client, test_db_session, monkeypatch):
    monkeypatch.setattr(
        "services.api.routes.auth.get_settings",
        lambda: SimpleNamespace(environment="development", frontend_url="http://localhost:3000"),
    )
    old_hash = hash_password("initial-pass")
    user = User(email=f"reset-{uuid4()}@example.com", hashed_password=old_hash)
    test_db_session.add(user)
    await test_db_session.commit()

    request = await client.post("/api/auth/password-reset/request", json={"email": user.email})
    assert request.status_code == 200
    token = request.json()["debug_token"]
    confirm = await client.post(
        "/api/auth/password-reset/confirm",
        json={"token": token, "password": "replacement-pass"},
    )
    assert confirm.status_code == 200
    await test_db_session.refresh(user)
    assert verify_password("replacement-pass", user.hashed_password)
    assert not verify_password("initial-pass", user.hashed_password)
    reused = await client.post(
        "/api/auth/password-reset/confirm",
        json={"token": token, "password": "another-pass"},
    )
    assert reused.status_code == 400
