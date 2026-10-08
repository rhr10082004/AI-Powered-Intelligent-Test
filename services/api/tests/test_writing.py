"""Writing evaluation persistence, validation and account isolation."""

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
async def test_writing_evaluation_is_saved_and_private(client, test_db_session, monkeypatch):
    monkeypatch.setattr("services.ai.writing.get_settings", lambda: SimpleNamespace(openai_api_key=None))
    owner = await create_user(test_db_session, f"writer-{uuid4()}@example.test")
    token = create_access_token(owner.id)
    essay = (
        "Education should encourage students to learn beyond examinations.\n\n"
        "First, projects help learners connect ideas with everyday life. For example, a science class can "
        "measure local water quality and discuss the results together. This makes abstract concepts easier "
        "to remember. In addition, collaboration helps students explain their thinking and consider other views.\n\n"
        "However, examinations still have a useful role because they give learners a clear goal and teachers "
        "a way to notice gaps. Schools can balance both approaches by using short tests alongside practical "
        "work. Therefore, students gain knowledge and learn how to apply it with confidence."
    )
    response = await client.post(
        "/api/writing/evaluate",
        params={"token": token},
        json={"exam_type": "IELTS", "prompt": "Should schools use projects?", "essay": essay},
    )
    assert response.status_code == 200
    result = response.json()
    assert result["evaluation_method"] == "rubric"
    assert len(result["feedback"]["criteria"]) == 4
    assert result["word_count"] >= 80

    own_history = await client.get("/api/writing/history", params={"token": token})
    assert own_history.status_code == 200
    assert len(own_history.json()) == 1
    assert own_history.json()[0]["id"] == result["id"]

    another_user = await create_user(test_db_session, f"reader-{uuid4()}@example.test")
    private_history = await client.get(
        "/api/writing/history", params={"token": create_access_token(another_user.id)}
    )
    assert private_history.status_code == 200
    assert private_history.json() == []


@pytest.mark.asyncio
async def test_writing_evaluation_requires_enough_words(client, test_db_session):
    user = await create_user(test_db_session, f"short-{uuid4()}@example.test")
    response = await client.post(
        "/api/writing/evaluate",
        params={"token": create_access_token(user.id)},
        json={"exam_type": "IELTS", "essay": "This draft is too short to receive useful feedback."},
    )
    assert response.status_code == 422
