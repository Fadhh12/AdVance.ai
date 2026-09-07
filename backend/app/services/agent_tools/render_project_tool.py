"""Wraps `project_service.enqueue_render` — the same path `POST /projects/{id}/render`
uses. Defaults to the user's most recently created project when `project_id` isn't
given.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.content_project import ContentProject
from app.models.user import User
from app.services.agent_tools.base import AgentTool
from app.services.errors import ProjectNotFoundError
from app.services.llm_providers.base import ToolSpec
from app.services.project_service import enqueue_render, get_owned_project


def _resolve_project_id(db: Session, current_user: User, project_id: str | None) -> uuid.UUID:
    if project_id is not None:
        return uuid.UUID(project_id)

    project = (
        db.execute(
            select(ContentProject)
            .where(ContentProject.user_id == current_user.id)
            .order_by(ContentProject.created_at.desc())
        )
        .scalars()
        .first()
    )
    if project is None:
        raise ProjectNotFoundError("Belum ada project yang bisa di-render.")
    return project.id


def _run(db: Session, current_user: User, arguments: dict) -> dict:
    project_id = _resolve_project_id(db, current_user, arguments.get("project_id"))

    motion_preset = arguments.get("motion_preset")
    if motion_preset:
        project = get_owned_project(project_id, db, current_user)
        project.motion_preset = motion_preset
        db.commit()

    project = enqueue_render(db, current_user, project_id)
    return {
        "project_id": str(project.id),
        "render_status": project.render_status,
        "motion_preset": project.motion_preset,
    }


TOOL = AgentTool(
    spec=ToolSpec(
        name="render_project_tool",
        description=(
            "Render video project via ffmpeg (default: project paling baru kalau "
            "project_id tidak disebut). Kalau motion_preset diisi (mis. "
            "'editorial-newspaper'), video dirender dengan gaya motion/transisi preset "
            "itu (punch zoom, whip pan, snap cut, dst) alih-alih trim polos."
        ),
        parameters={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "ID project (opsional)."},
                "motion_preset": {
                    "type": "string",
                    "description": (
                        "ID motion preset (opsional), mis. 'editorial-newspaper'. Lihat "
                        "GET /motion-presets untuk daftar lengkap."
                    ),
                },
            },
        },
    ),
    run=_run,
)
