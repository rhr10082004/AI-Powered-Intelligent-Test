"""AI Tutor API routes (Phase 3 scaffolding)."""

from __future__ import annotations

from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.database import get_db_session
from services.api.models import User
from services.api.utils.auth import verify_token
from services.ai.tutor import ChatMessage, tutor_chat

# --- Schemas (kept local to avoid touching existing schemas.py for Phase 3 scaffolding) ---

from pydantic import BaseModel


class TutorChatRequest(BaseModel):
    exam_type: Optional[str] = None
    messages: List[dict]


class TutorChatResponse(BaseModel):
    response: str


router = APIRouter(prefix="/tutor", tags=["tutor"])
AsyncSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


@router.post("/chat", response_model=TutorChatResponse)
async def tutor_chat_endpoint(
    payload: TutorChatRequest,
    token: str = Query(..., description="JWT access token"),
    db: AsyncSession = Depends(get_db_session),
) -> TutorChatResponse:
    """Chat with the AI tutor.

    Scaffolding endpoint: accepts messages and returns a placeholder response.

    Auth contract follows Phase 2 learning routes:
    - access token is supplied as a query param `token`
    """

    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Optional sanity check: user must exist
    user = await db.get(User, UUID(user_id)) if hasattr(db, "get") else None
    if user is None:
        # Not strictly required for placeholder behavior
        raise HTTPException(status_code=401, detail="Invalid token")

    # Convert incoming message dicts to ChatMessage dataclass
    chat_messages: List[ChatMessage] = []
    for m in payload.messages:
        role = m.get("role")
        content = m.get("content")
        if not role or not content:
            continue
        chat_messages.append(ChatMessage(role=str(role), content=str(content)))

    resp = await tutor_chat(
        exam_type=payload.exam_type,
        messages=chat_messages,
    )

    return TutorChatResponse(response=resp)

