"""Wraps `publish_service.enqueue_publish_manual` — the same path
`POST /projects/{id}/posts` uses. **Manual Assist only**: creates downloadable
per-platform exports + QR share for the user to upload themselves. It does NOT post to
Instagram/TikTok/YouTube automatically (CLAUDE.md: auto-posting isn't usable until
developer app approval lands) — the description below is shown to the LLM verbatim so
it never narrates this as real posting. Defaults to the user's most recently
successfully-rendered project when `project_id` isn't given.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.content_project import ContentProject
from app.models.user import User
from app.services.agent_tools.base import AgentTool
from app.services.errors import ProjectNotFoundError
from app.services.llm_providers.base import ToolSpec
from app.services.publish_service import enqueue_publish_manual


def _resolve_project_id(db: Session, current_user: User, project_id: str | None) -> uuid.UUID:
    if project_id is not None:
        return uuid.UUID(project_id)

    project = (
        db.execute(
            select(ContentProject)
            .where(
                ContentProject.user_id == current_user.id,
                ContentProject.render_status == "success",
            )
            .order_by(ContentProject.updated_at.desc())
        )
        .scalars()
        .first()
    )
    if project is None:
        raise ProjectNotFoundError(
            "Belum ada project yang sudah selesai di-render untuk disiapkan publish-nya."
        )
    return project.id


def _run(db: Session, current_user: User, arguments: dict) -> dict:
    project_id = _resolve_project_id(db, current_user, arguments.get("project_id"))
    posts = enqueue_publish_manual(db, current_user, project_id)
    return {"posts": [{"post_id": str(post.id), "platform": post.platform} for post in posts]}


TOOL = AgentTool(
    spec=ToolSpec(
        name="prepare_publish_tool",
        description=(
            "Siapkan export per platform (Instagram/TikTok/YouTube) dari project yang "
            "sudah di-render — hasilnya untuk diunduh & diupload manual oleh user "
            "(Publish Manual Assist). TIDAK memposting otomatis ke platform manapun."
        ),
        parameters={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "ID project (opsional)."}
            },
        },
    ),
    run=_run,
)
