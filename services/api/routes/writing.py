"""Writing evaluation and private submission history routes."""

from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.ai.writing import WritingFeedback, evaluate_writing
from services.api.activity import record_activity
from services.api.database import get_db_session
from services.api.models import User
from services.api.models_phase2_isolated import WritingSubmission
from services.api.utils.auth import verify_token

router = APIRouter(prefix="/writing", tags=["writing"])
AsyncSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


class WritingEvaluationRequest(BaseModel):
    exam_type: str = Field(default="IELTS", min_length=2, max_length=50)
    prompt: Optional[str] = Field(default=None, max_length=2000)
    essay: str = Field(min_length=100, max_length=20000)


class WritingEvaluationResponse(BaseModel):
    id: UUID
    exam_type: str
    word_count: int
    estimated_band: float
    evaluation_method: str
    feedback: WritingFeedback
    created_at: datetime

    class Config:
        from_attributes = True


class WritingHistoryItem(BaseModel):
    id: UUID
    exam_type: str
    prompt: Optional[str]
    essay_excerpt: str
    word_count: int
    estimated_band: float
    evaluation_method: str
    summary: str
    created_at: datetime


def _user_id(token: str) -> UUID:
    user_id = verify_token(token, "access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id


async def _require_user(db: AsyncSession, user_id: UUID) -> None:
    if await db.get(User, user_id) is None:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/evaluate", response_model=WritingEvaluationResponse)
async def evaluate_submission(
    payload: WritingEvaluationRequest,
    token: str = Query(..., description="JWT access token"),
    db: AsyncSession = Depends(get_db_session),
) -> WritingEvaluationResponse:
    user_id = _user_id(token)
    await _require_user(db, user_id)
    essay = payload.essay.strip()
    words = essay.split()
    if len(words) < 80:
        raise HTTPException(status_code=422, detail="Write at least 80 words so the feedback has enough context")

    score, feedback, method = await evaluate_writing(
        exam_type=payload.exam_type,
        prompt=(payload.prompt or "").strip(),
        essay=essay,
    )
    submission = WritingSubmission(
        id=uuid4(),
        user_id=user_id,
        exam_type=payload.exam_type.upper(),
        prompt=(payload.prompt or "").strip(),
        essay=essay,
        word_count=len(words),
        estimated_band=score,
        evaluation_method=method,
        feedback=feedback.model_dump(),
        created_at=datetime.utcnow(),
    )
    db.add(submission)
    record_activity(
        db,
        user_id=user_id,
        event_type="writing_evaluated",
        event_key=f"writing:{submission.id}",
        section="writing",
        reference_id=submission.id,
        details={"exam_type": submission.exam_type, "word_count": submission.word_count},
        points=5,
    )
    await db.commit()
    return WritingEvaluationResponse(
        id=submission.id,
        exam_type=submission.exam_type,
        word_count=submission.word_count,
        estimated_band=submission.estimated_band,
        evaluation_method=submission.evaluation_method,
        feedback=feedback,
        created_at=submission.created_at,
    )


@router.get("/history", response_model=list[WritingHistoryItem])
async def writing_history(
    token: str = Query(..., description="JWT access token"),
    db: AsyncSession = Depends(get_db_session),
) -> list[WritingHistoryItem]:
    user_id = _user_id(token)
    await _require_user(db, user_id)
    result = await db.execute(
        select(WritingSubmission)
        .where(WritingSubmission.user_id == user_id)
        .order_by(WritingSubmission.created_at.desc())
        .limit(20)
    )
    return [
        WritingHistoryItem(
            id=item.id,
            exam_type=item.exam_type,
            prompt=item.prompt or None,
            essay_excerpt=item.essay[:240],
            word_count=item.word_count,
            estimated_band=item.estimated_band,
            evaluation_method=item.evaluation_method,
            summary=item.feedback.get("summary", "Practice feedback saved."),
            created_at=item.created_at,
        )
        for item in result.scalars().all()
    ]
