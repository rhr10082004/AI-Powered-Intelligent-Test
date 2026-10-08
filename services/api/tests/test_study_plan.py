"""Daily study plans persist idempotently and remain private to each learner."""

from uuid import uuid4

import pytest

from services.api.models import User
from services.api.models_phase2_isolated import DailyStudyPlan
from services.api.utils.auth import create_access_token, hash_password


async def create_user(session, email):
    user = User(email=email, hashed_password=hash_password("safe-test-password"))
    session.add(user)
    await session.commit()
    return user


@pytest.mark.asyncio
async def test_daily_plan_is_created_once_and_tasks_are_owned(client, test_db_session):
    user = await create_user(test_db_session, f"planner-{uuid4()}@example.com")
    token = create_access_token(user.id)
    first = await client.post("/api/study-plan/today", params={"token": token}, json={"exam_type": "IELTS"})
    second = await client.post("/api/study-plan/today", params={"token": token}, json={"exam_type": "IELTS"})
    assert first.status_code == second.status_code == 200
    plan = first.json()
    assert plan["id"] == second.json()["id"]
    assert plan["target_minutes"] == sum(task["minutes"] for task in plan["tasks"])

    task = plan["tasks"][0]
    completed = await client.post(
        f"/api/study-plan/{plan['id']}/tasks/{task['id']}/complete", params={"token": token}
    )
    assert completed.status_code == 200
    assert next(item for item in completed.json()["tasks"] if item["id"] == task["id"])["completed"]
    repeated = await client.post(
        f"/api/study-plan/{plan['id']}/tasks/{task['id']}/complete", params={"token": token}
    )
    assert repeated.status_code == 200
    points = await client.get("/api/activity/summary", params={"token": token})
    assert points.json()["total_points"] == 1
    assert points.json()["total_events"] == 1

    other = await create_user(test_db_session, f"another-{uuid4()}@example.com")
    private = await client.post(
        f"/api/study-plan/{plan['id']}/tasks/{plan['tasks'][1]['id']}/complete",
        params={"token": create_access_token(other.id)},
    )
    assert private.status_code == 404
