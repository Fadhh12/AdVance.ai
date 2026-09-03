"""FR-05: lightweight editor — create a draft project from a completed generate job,
edit caption/music/trim, and render the trimmed result via ffmpeg.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.posts import post_to_out
from app.core.security import get_current_user
from app.models.ai_job import AIJob
from app.models.base import get_db
from app.models.content_project import ContentProject
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostOut
from app.schemas.project import ContentProjectCreate, ContentProjectOut, ContentProjectUpdate
from app.services.storage import generate_presigned_url
from app.services.video_render import PLATFORM_DURATION_LIMITS_SECONDS
from app.workers.tasks import export_post_task, render_project_task

router = APIRouter()


def _to_out(project: ContentProject, db: Session) -> ContentProjectOut:
    source_job = db.get(AIJob, project.source_job_id)
    return ContentProjectOut(
        id=project.id,
        title=project.title,
        mode=project.mode,
        status=project.status,
        caption=project.caption,
        music_track=project.music_track,
        trim_start_seconds=project.trim_start_seconds,
        trim_end_seconds=project.trim_end_seconds,
        render_status=project.render_status,
        render_error_message=project.render_error_message,
        source_video_url=source_job.result_url if source_job else "",
        final_video_url=(
            generate_presigned_url(project.final_video_url) if project.final_video_url else None
        ),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _get_owned_project(project_id: uuid.UUID, db: Session, current_user: User) -> ContentProject:
    project = db.execute(
        select(ContentProject).where(
            ContentProject.id == project_id, ContentProject.user_id == current_user.id
        )
    ).scalar_one_or_none()
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Project tidak ditemukan.")
    return project


@router.post("", response_model=ContentProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ContentProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    source_job = db.execute(
        select(AIJob).where(
            AIJob.id == payload.source_job_id, AIJob.user_id == current_user.id
        )
    ).scalar_one_or_none()
    if source_job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job generate tidak ditemukan.")
    if source_job.status != "success":
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Job generate belum selesai atau gagal."
        )

    project = ContentProject(
        user_id=current_user.id,
        title=payload.title,
        mode=payload.mode,
        source_job_id=source_job.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return _to_out(project, db)


@router.get("", response_model=list[ContentProjectOut])
def list_projects(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    projects = db.execute(
        select(ContentProject)
        .where(ContentProject.user_id == current_user.id)
        .order_by(ContentProject.created_at.desc())
    ).scalars()
    return [_to_out(project, db) for project in projects]


@router.get("/{project_id}", response_model=ContentProjectOut)
def get_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_owned_project(project_id, db, current_user)
    return _to_out(project, db)


@router.patch("/{project_id}", response_model=ContentProjectOut)
def update_project(
    project_id: uuid.UUID,
    payload: ContentProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_owned_project(project_id, db, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return _to_out(project, db)


@router.post(
    "/{project_id}/render", response_model=ContentProjectOut, status_code=status.HTTP_202_ACCEPTED
)
def render_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_owned_project(project_id, db, current_user)
    project.render_status = "queued"
    project.render_error_message = None
    db.commit()

    render_project_task.delay(str(project.id))
    db.refresh(project)  # eager mode in tests commits via a separate session (see conftest.py)

    return _to_out(project, db)


@router.post(
    "/{project_id}/posts", response_model=list[PostOut], status_code=status.HTTP_202_ACCEPTED
)
def create_posts(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """FR-13: prepares one export per platform (crop 9:16 + duration cap + caption
    adaptation) from the project's rendered final video. Requires a successful render
    first — there's nothing to export otherwise.
    """
    project = _get_owned_project(project_id, db, current_user)
    if project.render_status != "success":
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Render project dulu sebelum menyiapkan publish."
        )

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

    return [post_to_out(post, project) for post in posts]


@router.get("/{project_id}/posts", response_model=list[PostOut])
def list_posts(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_owned_project(project_id, db, current_user)
    posts = db.execute(
        select(Post).where(Post.project_id == project.id).order_by(Post.platform)
    ).scalars()
    return [post_to_out(post, project) for post in posts]
