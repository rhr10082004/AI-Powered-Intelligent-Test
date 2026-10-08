"""Helpers for appending private learner activity events."""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from services.api.models_phase2_isolated import ActivityEvent


def record_activity(
    session: AsyncSession,
    *,
    user_id: UUID,
    event_type: str,
    event_key: str | None = None,
    section: str | None = None,
    reference_id: UUID | None = None,
    details: dict[str, Any] | None = None,
    points: int = 0,
) -> ActivityEvent:
    """Stage a safe, idempotency-keyed event in the caller's transaction."""
    event = ActivityEvent(
        user_id=user_id,
        event_key=event_key or str(uuid4()),
        event_type=event_type,
        section=section,
        reference_id=reference_id,
        details=details or {},
        points=points,
        created_at=datetime.utcnow(),
    )
    session.add(event)
    return event
