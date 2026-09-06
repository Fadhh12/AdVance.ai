"""FR-03 (generate video) + FR-11 (quota, checked before the job runs, not after)."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.models.ai_job import AIJob
from app.models.base import get_db
from app.models.user import User
from app.schemas.ai import AIJobOut, GenerateVideoRequest
from app.services.errors import MediaNotFoundError, QuotaExceededError
from app.services.generation_service import create_generate_video_job

router = APIRouter()


@router.post(
    "/generate-video", response_model=AIJobOut, status_code=status.HTTP_202_ACCEPTED
)
def generate_video(
    payload: GenerateVideoRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        job = create_generate_video_job(
            db, current_user, payload.source_asset_id, payload.prompt
        )
    except MediaNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    except QuotaExceededError as exc:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, str(exc)) from exc

    return AIJobOut.model_validate(job)


@router.get("/jobs/{job_id}", response_model=AIJobOut)
def get_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.execute(
        select(AIJob).where(AIJob.id == job_id, AIJob.user_id == current_user.id)
    ).scalar_one_or_none()
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job tidak ditemukan.")
    return AIJobOut.model_validate(job)
