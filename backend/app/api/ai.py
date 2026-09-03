"""FR-03 (generate video) + FR-11 (quota, checked before the job runs, not after)."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import get_current_user
from app.models.ai_job import AIJob
from app.models.base import get_db
from app.models.media_asset import MediaAsset
from app.models.plan import Plan
from app.models.user import User
from app.schemas.ai import AIJobOut, GenerateVideoRequest
from app.workers.tasks import generate_video_task

router = APIRouter()


@router.post(
    "/generate-video", response_model=AIJobOut, status_code=status.HTTP_202_ACCEPTED
)
def generate_video(
    payload: GenerateVideoRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    source_asset = db.execute(
        select(MediaAsset).where(
            MediaAsset.id == payload.source_asset_id,
            MediaAsset.user_id == current_user.id,
        )
    ).scalar_one_or_none()
    if source_asset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Media sumber tidak ditemukan.")

    # SRS §2.2: cek kuota SEBELUM job dijalankan (bukan sesudah, biar tidak buang biaya).
    plan = db.get(Plan, current_user.plan_id) if current_user.plan_id else None
    if plan is None or current_user.ai_generation_used >= plan.ai_generation_quota:
        raise HTTPException(
            status.HTTP_402_PAYMENT_REQUIRED,
            "Kuota AI generation habis untuk paket kamu saat ini.",
        )

    job = AIJob(
        user_id=current_user.id,
        source_asset_id=source_asset.id,
        type="generate_video",
        status="queued",
        provider=get_settings().ai_video_provider,
        prompt=payload.prompt,
    )
    db.add(job)
    current_user.ai_generation_used += 1
    db.commit()
    db.refresh(job)

    generate_video_task.delay(str(job.id))
    # In production this is a same-state no-op (the real worker hasn't run yet); in
    # tests Celery runs eagerly via a separate DB session (see conftest.py), so
    # without this refresh the response would still show the pre-task "queued" state.
    db.refresh(job)

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
