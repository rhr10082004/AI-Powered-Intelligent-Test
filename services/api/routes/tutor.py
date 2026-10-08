"""AI tutor API routes with private, persistent conversation history."""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Annotated, Literal, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from services.ai.tutor import ChatMessage, tutor_chat
from services.api.database import get_db_session
from services.api.models import User
from services.api.models_phase2_isolated import (
    GrammarTopic,
    Passage,
    TutorConversation,
    TutorMessage,
    VocabularyWord,
)
from services.api.utils.auth import verify_token

router = APIRouter(prefix="/tutor", tags=["tutor"])
AsyncSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


class TutorMessageInput(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=12000)


class TutorChatRequest(BaseModel):
    exam_type: Optional[str] = Field(default=None, max_length=50)
    conversation_id: Optional[UUID] = None
    messages: list[TutorMessageInput] = Field(min_length=1, max_length=30)


class TutorChatResponse(BaseModel):
    response: str
    conversation_id: UUID


class TutorConversationSummary(BaseModel):
    id: UUID
    title: str
    exam_type: Optional[str]
    updated_at: datetime

    class Config:
        from_attributes = True


class TutorMessageResponse(BaseModel):
    id: UUID
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class TutorConversationDetail(TutorConversationSummary):
    messages: list[TutorMessageResponse]


def _user_id_from_token(token: str) -> UUID:
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id


async def _require_user(db: AsyncSession, user_id: UUID) -> None:
    if await db.get(User, user_id) is None:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/conversations", response_model=list[TutorConversationSummary])
async def list_conversations(
    token: str = Query(..., description="JWT access token"),
    db: AsyncSession = Depends(get_db_session),
) -> list[TutorConversationSummary]:
    user_id = _user_id_from_token(token)
    await _require_user(db, user_id)
    result = await db.execute(
        select(TutorConversation)
        .where(TutorConversation.user_id == user_id)
        .order_by(TutorConversation.updated_at.desc())
        .limit(50)
    )
    return list(result.scalars().all())


@router.get("/conversations/{conversation_id}", response_model=TutorConversationDetail)
async def get_conversation(
    conversation_id: UUID,
    token: str = Query(..., description="JWT access token"),
    db: AsyncSession = Depends(get_db_session),
) -> TutorConversationDetail:
    user_id = _user_id_from_token(token)
    await _require_user(db, user_id)
    result = await db.execute(
        select(TutorConversation).where(
            TutorConversation.id == conversation_id,
            TutorConversation.user_id == user_id,
        )
    )
    conversation = result.scalar_one_or_none()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    message_result = await db.execute(
        select(TutorMessage)
        .where(TutorMessage.conversation_id == conversation.id)
        .order_by(TutorMessage.created_at)
        .limit(200)
    )
    return TutorConversationDetail(
        id=conversation.id,
        title=conversation.title,
        exam_type=conversation.exam_type,
        updated_at=conversation.updated_at,
        messages=list(message_result.scalars().all()),
    )


@router.post("/chat", response_model=TutorChatResponse)
async def tutor_chat_endpoint(
    payload: TutorChatRequest,
    token: str = Query(..., description="JWT access token"),
    db: AsyncSession = Depends(get_db_session),
) -> TutorChatResponse:
    user_id = _user_id_from_token(token)
    await _require_user(db, user_id)

    chat_messages = [ChatMessage(role=item.role, content=item.content.strip()) for item in payload.messages]
    last_user_message = next(
        (message.content for message in reversed(chat_messages) if message.role == "user"),
        "",
    )
    if not last_user_message:
        raise HTTPException(status_code=422, detail="Add a question before sending a message")

    conversation: Optional[TutorConversation] = None
    if payload.conversation_id is not None:
        result = await db.execute(
            select(TutorConversation).where(
                TutorConversation.id == payload.conversation_id,
                TutorConversation.user_id == user_id,
            )
        )
        conversation = result.scalar_one_or_none()
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        title = " ".join(last_user_message.split())[:197]
        if len(last_user_message) > 197:
            title += "..."
        conversation = TutorConversation(
            id=uuid4(),
            user_id=user_id,
            title=title,
            exam_type=payload.exam_type,
        )
        db.add(conversation)
        await db.flush()

    search_terms = list(
        dict.fromkeys(
            term
            for term in re.findall(r"[a-zA-Z]{4,}", last_user_message.casefold())
            if term not in {"what", "when", "where", "which", "would", "could", "should", "please", "help"}
        )
    )[:5]
    retrieved_context: list[str] = []
    if search_terms:
        passage_match = or_(*[
            Passage.title.ilike(f"%{term}%") | Passage.content.ilike(f"%{term}%")
            for term in search_terms
        ])
        passage_query = select(Passage.title, Passage.content).where(passage_match)
        if payload.exam_type:
            passage_query = passage_query.where(Passage.exam_type.ilike(payload.exam_type))
        passage_rows = await db.execute(passage_query.limit(2))
        retrieved_context.extend(
            f"Reading passage '{title}': {content[:700]}"
            for title, content in passage_rows.all()
        )

        vocabulary_match = or_(*[
            VocabularyWord.word.ilike(f"%{term}%") | VocabularyWord.definition.ilike(f"%{term}%")
            for term in search_terms
        ])
        vocabulary_query = select(VocabularyWord.word, VocabularyWord.definition).where(vocabulary_match)
        if payload.exam_type:
            vocabulary_query = vocabulary_query.where(VocabularyWord.exam_type.ilike(payload.exam_type))
        vocabulary_rows = await db.execute(vocabulary_query.limit(3))
        retrieved_context.extend(
            f"Vocabulary '{word}': {definition}"
            for word, definition in vocabulary_rows.all()
        )

        grammar_match = or_(*[
            GrammarTopic.topic_name.ilike(f"%{term}%")
            | GrammarTopic.description.ilike(f"%{term}%")
            | GrammarTopic.explanation.ilike(f"%{term}%")
            for term in search_terms
        ])
        grammar_query = select(GrammarTopic.topic_name, GrammarTopic.explanation).where(grammar_match)
        if payload.exam_type:
            grammar_query = grammar_query.where(GrammarTopic.exam_type.ilike(payload.exam_type))
        grammar_rows = await db.execute(grammar_query.limit(2))
        retrieved_context.extend(
            f"Grammar topic '{topic}': {explanation}"
            for topic, explanation in grammar_rows.all()
            if explanation
        )

    response = await tutor_chat(
        exam_type=payload.exam_type,
        messages=chat_messages,
        retrieved_context=retrieved_context,
    )
    now = datetime.utcnow()
    conversation.updated_at = now
    db.add_all([
        TutorMessage(conversation_id=conversation.id, role="user", content=last_user_message, created_at=now),
        TutorMessage(conversation_id=conversation.id, role="assistant", content=response, created_at=now + timedelta(microseconds=1)),
    ])
    await db.commit()
    return TutorChatResponse(response=response, conversation_id=conversation.id)


