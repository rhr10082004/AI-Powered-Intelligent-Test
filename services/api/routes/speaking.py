"""Transcript-based speaking practice with private learner history."""

import re
from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.activity import record_activity
from services.api.database import get_db_session
from services.api.models import User
from services.api.models_phase2_isolated import SpeakingSubmission
from services.api.utils.auth import verify_token

router = APIRouter(prefix="/speaking", tags=["speaking"])
AsyncSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


class SpeakingRequest(BaseModel):
    exam_type: str = Field(default="IELTS", min_length=2, max_length=50)
    prompt: str = Field(min_length=5, max_length=1000)
    transcript: str = Field(min_length=80, max_length=12000)


class SpeakingCriterion(BaseModel):
    name: str
    score: float
    feedback: str


class SpeakingFeedback(BaseModel):
    summary: str
    criteria: list[SpeakingCriterion]
    strengths: list[str]
    next_steps: list[str]
    limitation: str


class SpeakingResponse(BaseModel):
    id: UUID
    exam_type: str
    prompt: str
    word_count: int
    estimated_score: float
    feedback: SpeakingFeedback
    created_at: datetime


class SpeakingHistoryItem(BaseModel):
    id: UUID
    exam_type: str
    prompt: str
    transcript_excerpt: str
    word_count: int
    estimated_score: float
    summary: str
    created_at: datetime


async def _learner(db: AsyncSession, token: str) -> UUID:
    user_id = verify_token(token, "access")
    if not user_id or await db.get(User, user_id) is None:
        raise HTTPException(status_code=401, detail="Sign in to save speaking practice.")
    return user_id


def _review(transcript: str) -> tuple[float, dict]:
    words = re.findall(r"\b[\w'-]+\b", transcript)
    sentences = [part.strip() for part in re.split(r"[.!?]+", transcript) if part.strip()]
    lower = transcript.casefold()
    connectors = [word for word in ("because", "however", "for example", "therefore", "although", "first", "finally", "as a result") if word in lower]
    repeats = len(words) - len(set(word.casefold() for word in words))
    criteria = [
        {"name": "Response development", "score": min(5, 2 + len(words) // 45), "feedback": "Add a specific example or detail to develop your main point." if len(words) < 100 else "You gave your response enough detail to develop the main idea."},
        {"name": "Organization", "score": min(5, 2 + len(connectors)), "feedback": "Use signposting such as 'first', 'because', or 'for example' to connect ideas." if len(connectors) < 2 else "Your response uses transitions to guide the listener."},
        {"name": "Sentence variety", "score": min(5, max(2, 2 + len(sentences) // 4)), "feedback": "Try mixing short statements with a few longer explanations." if len(sentences) < 4 else "You used several sentence units to structure the response."},
        {"name": "Word choice", "score": min(5, max(2, 5 - repeats // max(1, len(words) // 12))), "feedback": "Look for repeated key words and replace some with precise alternatives." if repeats > len(words) // 2 else "Your transcript shows a useful range of words for the response."},
    ]
    score = round(sum(item["score"] for item in criteria) / len(criteria), 1)
    feedback = {
        "summary": "A transcript-based practice review. Use the notes below to plan another attempt.",
        "criteria": criteria,
        "strengths": ["You completed a response to the prompt.", "Your transcript contains about {} words.".format(len(words))],
        "next_steps": [item["feedback"] for item in criteria if item["score"] < 4][:3] or ["Try the prompt again with a new example and a clear closing sentence."],
        "limitation": "This review analyzes the transcript only. It cannot assess pronunciation, pace, intonation, or accent and is not an official exam score.",
    }
    return score, feedback


@router.post("/evaluate", response_model=SpeakingResponse)
async def evaluate_speaking(payload: SpeakingRequest, token: str = Query(...), db: AsyncSession = Depends(get_db_session)) -> SpeakingResponse:
    user_id = await _learner(db, token)
    transcript = payload.transcript.strip()
    words = re.findall(r"\b[\w'-]+\b", transcript)
    if len(words) < 20:
        raise HTTPException(status_code=422, detail="Speak or type at least 20 words for a useful review.")
    score, feedback = _review(transcript)
    submission = SpeakingSubmission(id=uuid4(), user_id=user_id, exam_type=payload.exam_type.upper(), prompt=payload.prompt.strip(), transcript=transcript, estimated_score=score, feedback=feedback, created_at=datetime.utcnow())
    db.add(submission)
    record_activity(db, user_id=user_id, event_type="speaking_evaluated", event_key=f"speaking:{submission.id}", section="speaking", reference_id=submission.id, details={"exam_type": submission.exam_type, "word_count": len(words)}, points=5)
    await db.commit()
    return SpeakingResponse(id=submission.id, exam_type=submission.exam_type, prompt=submission.prompt, word_count=len(words), estimated_score=score, feedback=SpeakingFeedback(**feedback), created_at=submission.created_at)


@router.get("/history", response_model=list[SpeakingHistoryItem])
async def speaking_history(token: str = Query(...), db: AsyncSession = Depends(get_db_session)) -> list[SpeakingHistoryItem]:
    user_id = await _learner(db, token)
    result = await db.execute(select(SpeakingSubmission).where(SpeakingSubmission.user_id == user_id).order_by(SpeakingSubmission.created_at.desc()).limit(20))
    items = result.scalars().all()
    return [SpeakingHistoryItem(id=item.id, exam_type=item.exam_type, prompt=item.prompt, transcript_excerpt=item.transcript[:220], word_count=len(re.findall(r"\b[\w'-]+\b", item.transcript)), estimated_score=item.estimated_score, summary=item.feedback.get("summary", "Speaking practice saved."), created_at=item.created_at) for item in items]
