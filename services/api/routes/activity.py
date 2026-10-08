"""Private activity feed and points summary."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.database import get_db_session
from services.api.models_phase2_isolated import ActivityEvent
from services.api.utils.auth import verify_token

router = APIRouter(prefix="/activity", tags=["activity"])


class ActivityEventResponse(BaseModel):
    id: UUID
    event_type: str
    section: Optional[str]
    reference_id: Optional[UUID]
    details: dict
    points: int
    created_at: datetime

    class Config:
        from_attributes = True


class ActivitySummaryResponse(BaseModel):
    total_points: int
    level: int
    points_to_next_level: int
    total_events: int
    events_last_7_days: int


def _authenticated_user(token: str) -> UUID:
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id


@router.get("/my-events", response_model=list[ActivityEventResponse])
async def list_my_activity(
    token: str = Query(...),
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session),
) -> list[ActivityEventResponse]:
    user_id = _authenticated_user(token)
    result = await db.execute(
        select(ActivityEvent)
        .where(ActivityEvent.user_id == user_id)
        .order_by(ActivityEvent.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


@router.get("/summary", response_model=ActivitySummaryResponse)
async def my_activity_summary(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db_session),
) -> ActivitySummaryResponse:
    user_id = _authenticated_user(token)
    totals = await db.execute(
        select(
            func.coalesce(func.sum(ActivityEvent.points), 0),
            func.count(ActivityEvent.id),
        ).where(ActivityEvent.user_id == user_id)
    )
    total_points, total_events = totals.one()
    recent = await db.scalar(
        select(func.count(ActivityEvent.id)).where(
            ActivityEvent.user_id == user_id,
            ActivityEvent.created_at >= datetime.utcnow() - timedelta(days=7),
        )
    )
    total_points = int(total_points or 0)
    return ActivitySummaryResponse(
        total_points=total_points,
        level=(total_points // 100) + 1,
        points_to_next_level=100 - (total_points % 100),
        total_events=int(total_events or 0),
        events_last_7_days=int(recent or 0),
    )
