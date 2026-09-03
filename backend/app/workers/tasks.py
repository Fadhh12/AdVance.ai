"""Celery tasks. Each task opens its own DB session via `models_base.SessionLocal()`
(attribute access, not a direct import) so tests can swap in a test session factory —
see tests/conftest.py.
"""
import io
import logging
import uuid
from datetime import UTC, datetime

from app.models import base as models_base
from app.models.ai_job import AIJob
from app.models.content_project import ContentProject
from app.models.media_asset import MediaAsset
from app.services.ai_providers.base import TransientProviderError
from app.services.ai_providers.factory import get_video_provider
from app.services.storage import generate_presigned_url, upload_object
from app.services.video_render import FFmpegNotAvailableError, VideoRenderError, trim_video
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.tasks.ping")
def ping() -> str:
    return "pong"


@celery_app.task(
    name="app.workers.tasks.generate_video_task",
    autoretry_for=(TransientProviderError,),
    retry_backoff=True,
    retry_backoff_max=60,
    max_retries=3,  # SRS §2.3: max 3x retry w/ backoff for transient errors only
)
def generate_video_task(job_id: str) -> None:
    db = models_base.SessionLocal()
    try:
        job = db.get(AIJob, uuid.UUID(job_id))
        if job is None:
            logger.error("generate_video_task: job %s not found", job_id)
            return

        job.status = "processing"
        db.commit()

        source_asset = db.get(MediaAsset, job.source_asset_id)
        if source_asset is None:
            job.status = "failed"
            job.error_message = "Media sumber tidak ditemukan."
            job.completed_at = datetime.now(UTC)
            db.commit()
            return

        source_image_url = generate_presigned_url(source_asset.file_url)
        result = get_video_provider().generate_video(source_image_url, prompt=job.prompt)

        if result.success:
            job.status = "success"
            job.result_url = result.result_url
        else:
            job.status = "failed"
            job.error_message = result.error_message or "Provider gagal generate video."
        job.completed_at = datetime.now(UTC)
        db.commit()
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.render_project_task")
def render_project_task(project_id: str) -> None:
    db = models_base.SessionLocal()
    try:
        project = db.get(ContentProject, uuid.UUID(project_id))
        if project is None:
            logger.error("render_project_task: project %s not found", project_id)
            return

        project.render_status = "processing"
        db.commit()

        source_job = db.get(AIJob, project.source_job_id)
        if source_job is None or not source_job.result_url:
            project.render_status = "failed"
            project.render_error_message = "Video sumber (hasil generate) tidak ditemukan."
            db.commit()
            return

        try:
            video_bytes = trim_video(
                source_job.result_url, project.trim_start_seconds, project.trim_end_seconds
            )
        except (FFmpegNotAvailableError, VideoRenderError) as exc:
            project.render_status = "failed"
            project.render_error_message = str(exc)
            db.commit()
            return

        key = f"renders/{project.id}/{uuid.uuid4()}.mp4"
        upload_object(key, io.BytesIO(video_bytes), "video/mp4")

        project.final_video_url = key
        project.render_status = "success"
        db.commit()
    finally:
        db.close()
