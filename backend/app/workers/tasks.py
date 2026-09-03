"""Phase 1: one no-op task to prove the worker/broker wiring is correct end-to-end.
Real tasks (`generate_video_task`, `publish_post_task`, ...) land here in later phases.
"""
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.ping")
def ping() -> str:
    return "pong"
