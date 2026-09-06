"""Publish Manual Assist enqueueing (FR-13) — extracted from `app/api/projects.py`
(Phase 6R) so the AI chat agent's `prepare_publish_tool` calls the exact same path as
the HTTP endpoint. **Manual Assist only**: this creates per-platform exports + QR
share for the user to upload themselves — it never posts to Instagram/TikTok/YouTube
automatically (CLAUDE.md: auto-posting isn't usable until developer app approval
lands). Any caller, including the chat agent, must never narrate this as real posting.
"""
import uuid

from sqlalchemy.orm import Session

from app.models.post import Post
from app.models.user import User
from app.services.errors import RenderNotReadyError
from app.services.project_service import get_owned_project
from app.services.video_render import PLATFORM_DURATION_LIMITS_SECONDS
from app.workers.tasks import export_post_task


def enqueue_publish_manual(db: Session, current_user: User, project_id: uuid.UUID) -> list[Post]:
    project = get_owned_project(project_id, db, current_user)
    if project.render_status != "success":
        raise RenderNotReadyError("Render project dulu sebelum menyiapkan publish.")

    posts = [
        Post(project_id=project.id, platform=platform, export_status="queued")
        for platform in PLATFORM_DURATION_LIMITS_SECONDS
    ]
    db.add_all(posts)
    db.commit()

    for post in posts:
        db.refresh(post)
        export_post_task.delay(str(post.id))
        db.refresh(post)  # eager mode in tests — reflect the task's own commit

    return posts
