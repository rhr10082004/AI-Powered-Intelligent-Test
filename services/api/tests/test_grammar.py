"""Grammar answer persistence and account scoped history."""

from uuid import uuid4

import pytest

from services.api.models import User
from services.api.models_phase2_isolated import GrammarExercise, GrammarTopic
from services.api.utils.auth import create_access_token, hash_password


async def create_user(session, email):
    user = User(email=email, hashed_password=hash_password("safe-test-password"))
    session.add(user)
    await session.commit()
    return user


@pytest.mark.asyncio
async def test_grammar_attempts_are_saved_and_private(client, test_db_session):
    owner = await create_user(test_db_session, f"grammar-{uuid4()}@example.test")
    topic = GrammarTopic(
        topic_name=f"Verb forms {uuid4()}",
        description="Practice verb agreement.",
        explanation="Match the verb to its subject.",
        examples=[],
        exam_type="IELTS",
        difficulty="easy",
        order=1,
    )
    exercise = GrammarExercise(
        topic=topic,
        sentence="She ___ to class every morning. (walk)",
        correct_form="walks",
        explanation="Use the third-person singular form.",
        difficulty="easy",
        hint="She is third-person singular.",
    )
    test_db_session.add(topic)
    await test_db_session.commit()
    await test_db_session.refresh(exercise)
    token = create_access_token(owner.id)

    first = await client.post(
        "/api/grammar/exercises/answer",
        params={"token": token},
        json={"exercise_id": str(exercise.id), "user_answer": "walk"},
    )
    second = await client.post(
        "/api/grammar/exercises/answer",
        params={"token": token},
        json={"exercise_id": str(exercise.id), "user_answer": "walks"},
    )
    assert first.status_code == second.status_code == 200
    assert first.json()["attempt_number"] == 1
    assert second.json()["attempt_number"] == 2
    assert first.json()["is_correct"] is False
    assert second.json()["is_correct"] is True

    own_history = await client.get("/api/grammar/my-attempts", params={"token": token})
    assert own_history.status_code == 200
    assert len(own_history.json()) == 2
    assert {item["user_answer"] for item in own_history.json()} == {"walk", "walks"}

    other = await create_user(test_db_session, f"another-{uuid4()}@example.test")
    private_history = await client.get(
        "/api/grammar/my-attempts", params={"token": create_access_token(other.id)}
    )
    assert private_history.status_code == 200
    assert private_history.json() == []
