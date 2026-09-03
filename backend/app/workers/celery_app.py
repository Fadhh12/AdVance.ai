"""Celery app instance (SDD §3.1: Celery + Redis for async AI generation & publishing).
Run a worker with: `celery -A app.workers.celery_app worker --loglevel=info`
(needs Redis — `docker compose up -d` — not yet runnable on this machine, see PROGRESS.md).
"""
from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "advance_ai",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.autodiscover_tasks(["app.workers"])
