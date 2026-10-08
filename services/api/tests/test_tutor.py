"""Integration coverage for saved tutor conversations."""

from types import SimpleNamespace
from uuid import uuid4

import pytest

from services.api.models import User
from services.api.utils.auth import create_access_token, hash_password


async def create_user(session, email):
    user = User(email=email, hashed_password=hash_password("safe-test-password"))
    session.add(user)
    await session.commit()
    return user


@pytest.mark.asyncio
async def test_tutor_conversations_are_saved_and_private(client, test_db_session, monkeypatch):
    monkeypatch.setattr(
        "services.ai.tutor.get_settings",
        lambda: SimpleNamespace(openai_api_key=None),
    )
    owner = await create_user(test_db_session, f"owner-{uuid4()}@example.test")
    owner_token = create_access_token(owner.id)

    response = await client.post(
        "/api/tutor/chat",
        params={"token": owner_token},
        json={
            "exam_type": "IELTS",
            "messages": [{"role": "user", "content": "How can I improve my reading practice?"}],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    conversation_id = payload["conversation_id"]
    assert payload["response"]

    second_turn = await client.post(
        "/api/tutor/chat",
        params={"token": owner_token},
        json={
            "exam_type": "IELTS",
            "conversation_id": conversation_id,
            "messages": [
                {"role": "user", "content": "How can I improve my reading practice?"},
                {"role": "assistant", "content": payload["response"]},
                {"role": "user", "content": "What should I do with mistakes?"},
            ],
        },
    )
    assert second_turn.status_code == 200

    history = await client.get("/api/tutor/conversations", params={"token": owner_token})
    assert history.status_code == 200
    assert len(history.json()) == 1
    assert history.json()[0]["id"] == conversation_id

    detail = await client.get(
        f"/api/tutor/conversations/{conversation_id}",
        params={"token": owner_token},
    )
    assert detail.status_code == 200
    assert [message["role"] for message in detail.json()["messages"]] == [
        "user", "assistant", "user", "assistant"
    ]

    other_user = await create_user(test_db_session, f"other-{uuid4()}@example.test")
    other_token = create_access_token(other_user.id)
    private_detail = await client.get(
        f"/api/tutor/conversations/{conversation_id}",
        params={"token": other_token},
    )
    assert private_detail.status_code == 404
