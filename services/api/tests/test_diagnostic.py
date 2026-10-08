"""Diagnostic question banks hide answer keys and save a baseline session."""

from uuid import uuid4

import pytest

from services.api.models import User
from services.api.seed import seed_learning_content
from services.api.utils.auth import create_access_token, hash_password


@pytest.mark.asyncio
async def test_diagnostic_banks_cover_supported_exams_and_complete_a_session(
    client, test_db_session, test_session_factory
):
    await seed_learning_content(test_session_factory)
    user = User(email=f"diagnostic-{uuid4()}@example.com", hashed_password=hash_password("safe-test-password"))
    test_db_session.add(user)
    await test_db_session.commit()
    token = create_access_token(user.id)

    for exam in ("IELTS", "GRE", "TOEFL"):
        response = await client.get(
            "/api/diagnostic/questions", params={"token": token, "exam_type": exam}
        )
        assert response.status_code == 200
        question_set = response.json()
        assert question_set["exam_type"] == exam
        assert len(question_set["questions"]) == 5
        assert all(
            "is_correct" not in answer and "explanation" not in answer
            for question in question_set["questions"]
            for answer in question["answers"]
        )

    selected = await client.get(
        "/api/diagnostic/questions", params={"token": token, "exam_type": "IELTS"}
    )
    session_id = str(uuid4())
    saved_attempts = []
    for question in selected.json()["questions"]:
        saved = await client.post(
            "/api/questions/answer",
            params={"token": token},
            json={
                "question_id": question["id"],
                "answer_id": question["answers"][0]["id"],
                "session_id": session_id,
            },
        )
        assert saved.status_code == 200
        saved_attempts.append(saved.json())

    retried = await client.post(
        "/api/questions/answer",
        params={"token": token},
        json={
            "question_id": selected.json()["questions"][0]["id"],
            "answer_id": selected.json()["questions"][0]["answers"][0]["id"],
            "session_id": session_id,
        },
    )
    assert retried.status_code == 200
    assert retried.json()["id"] == saved_attempts[0]["id"]
    completed = await client.post(
        "/api/study-sessions/complete",
        params={"token": token},
        json={"session_id": session_id, "section": "reading", "duration": 180},
    )
    assert completed.status_code == 200
    assert completed.json()["questions_attempted"] == 5

    activity = await client.get("/api/activity/my-events", params={"token": token})
    summary = await client.get("/api/activity/summary", params={"token": token})
    assert activity.status_code == summary.status_code == 200
    assert len(activity.json()) == 6
    assert summary.json()["total_points"] == 10
    assert summary.json()["level"] == 1

    another = User(email=f"private-{uuid4()}@example.com", hashed_password=hash_password("safe-test-password"))
    test_db_session.add(another)
    await test_db_session.commit()
    other_activity = await client.get(
        "/api/activity/my-events", params={"token": create_access_token(another.id)}
    )
    assert other_activity.status_code == 200
    assert other_activity.json() == []


@pytest.mark.asyncio
async def test_diagnostic_requires_authentication(client):
    response = await client.get("/api/diagnostic/questions", params={"exam_type": "IELTS"})
    assert response.status_code == 422
