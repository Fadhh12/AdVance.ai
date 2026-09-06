"""Project creation from a completed generate job, and render enqueueing (FR-05) —
extracted from `app/api/projects.py` (Phase 6R) so the AI chat agent's
`create_project_tool`/`render_project_tool` call the exact same path as the HTTP
endpoints. `get_owned_project` is also reused directly by `app/api/projects.py` for
its other routes and by `app/services/publish_service.py`, instead of every caller
re-implementing the ownership-scoped lookup.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai_job import AIJob
from app.models.content_project import ContentProject
from app.models.user import User
from app.services.errors import JobNotFoundError, JobNotReadyError, ProjectNotFoundError
from app.workers.tasks import render_project_task


def get_owned_project(project_id: uuid.UUID, db: Session, current_user: User) -> ContentProject:
    project = db.execute(
        select(ContentProject).where(
            ContentProject.id == project_id, ContentProject.user_id == current_user.id
        )
    ).scalar_one_or_none()
    if project is None:
        raise ProjectNotFoundError("Project tidak ditemukan.")
    return project


def create_project_from_job(
    db: Session, current_user: User, title: str, mode: str, source_job_id: uuid.UUID
) -> ContentProject:
    source_job = db.execute(
        select(AIJob).where(AIJob.id == source_job_id, AIJob.user_id == current_user.id)
    ).scalar_one_or_none()
    if source_job is None:
        raise JobNotFoundError("Job generate tidak ditemukan.")
    if source_job.status != "success":
        raise JobNotReadyError("Job generate belum selesai atau gagal.")

    project = ContentProject(
        user_id=current_user.id,
        title=title,
        mode=mode,
        source_job_id=source_job.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def enqueue_render(db: Session, current_user: User, project_id: uuid.UUID) -> ContentProject:
    project = get_owned_project(project_id, db, current_user)
    project.render_status = "queued"
    project.render_error_message = None
    db.commit()

    render_project_task.delay(str(project.id))
    db.refresh(project)  # eager mode in tests commits via a separate session (see conftest.py)

    return project
