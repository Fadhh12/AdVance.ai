"""Generate-video job creation (FR-03 + FR-11 quota check) — extracted from
`app/api/ai.py` (Phase 6R) so the AI chat agent's `generate_video_tool` can create a
real `AIJob` through the exact same path as the HTTP endpoint, instead of
re-implementing the quota/enqueue logic a second time.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.ai_job import AIJob
from app.models.media_asset import MediaAsset
from app.models.plan import Plan
from app.models.user import User
from app.services.errors import MediaNotFoundError, QuotaExceededError
from app.workers.tasks import generate_video_task


def create_generate_video_job(
    db: Session, current_user: User, source_asset_id: uuid.UUID, prompt: str | None
) -> AIJob:
    source_asset = db.execute(
        select(MediaAsset).where(
            MediaAsset.id == source_asset_id,
            MediaAsset.user_id == current_user.id,
        )
    ).scalar_one_or_none()
    if source_asset is None:
        raise MediaNotFoundError("Media sumber tidak ditemukan.")

    # SRS §2.2: cek kuota SEBELUM job dijalankan (bukan sesudah, biar tidak buang biaya).
    plan = db.get(Plan, current_user.plan_id) if current_user.plan_id else None
    if plan is None or current_user.ai_generation_used >= plan.ai_generation_quota:
        raise QuotaExceededError("Kuota AI generation habis untuk paket kamu saat ini.")

    job = AIJob(
        user_id=current_user.id,
        source_asset_id=source_asset.id,
        type="generate_video",
        status="queued",
        provider=get_settings().ai_video_provider,
        prompt=prompt,
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

    return job
