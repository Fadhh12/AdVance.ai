"""FR-13/FR-14: single-post operations for Publish Manual Assist — mark as manually
uploaded, and get a QR code for the "share to phone" flow. Batch creation/listing of
posts under a project lives in app/api/projects.py (needs project ownership context).
"""
import io
import uuid

import qrcode
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.models.base import get_db
from app.models.content_project import ContentProject
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostOut
from app.services.caption_adapter import youtube_title
from app.services.storage import generate_presigned_url

router = APIRouter()


def post_to_out(post: Post, project: ContentProject | None = None) -> PostOut:
    return PostOut(
        id=post.id,
        project_id=post.project_id,
        platform=post.platform,
        export_status=post.export_status,
        export_error_message=post.export_error_message,
        caption=post.caption,
        youtube_title=(
            youtube_title(project.title) if post.platform == "youtube" and project else None
        ),
        video_url=generate_presigned_url(post.video_key) if post.video_key else None,
        status=post.status,
        created_at=post.created_at,
    )


def _get_owned_post(post_id: uuid.UUID, db: Session, current_user: User) -> Post:
    post = db.execute(
        select(Post)
        .join(ContentProject, Post.project_id == ContentProject.id)
        .where(Post.id == post_id, ContentProject.user_id == current_user.id)
    ).scalar_one_or_none()
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post tidak ditemukan.")
    return post


@router.post("/{post_id}/mark-uploaded", response_model=PostOut)
def mark_uploaded(
    post_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = _get_owned_post(post_id, db, current_user)
    if post.status != "manual_ready":
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Video belum siap (export belum sukses)."
        )
    post.status = "manual_uploaded"
    db.commit()
    db.refresh(post)
    return post_to_out(post, db.get(ContentProject, post.project_id))


@router.get("/{post_id}/qr", response_class=Response)
def get_share_qr(
    post_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """PNG QR code encoding a signed download URL — scan on a phone to grab the file
    without needing the desktop browser session (FR-13: "share to phone").
    """
    post = _get_owned_post(post_id, db, current_user)
    if not post.video_key:
        raise HTTPException(status.HTTP_409_CONFLICT, "Video belum siap (export belum sukses).")

    download_url = generate_presigned_url(post.video_key)
    image = qrcode.make(download_url)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    return Response(content=buffer.getvalue(), media_type="image/png")
