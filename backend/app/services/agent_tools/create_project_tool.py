"""Wraps `project_service.create_project_from_job` — the same path `POST /projects`
uses. Defaults to the user's most recently successful generate job when `job_id` isn't
given, so "lanjut ke editor" works right after a `generate_video_tool` call in the
same conversation without the LLM having to carry the id forward itself.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai_job import AIJob
from app.models.user import User
from app.services.agent_tools.base import AgentTool
from app.services.errors import JobNotFoundError
from app.services.llm_providers.base import ToolSpec
from app.services.project_service import create_project_from_job


def _resolve_job_id(db: Session, current_user: User, job_id: str | None) -> uuid.UUID:
    if job_id is not None:
        return uuid.UUID(job_id)

    job = (
        db.execute(
            select(AIJob)
            .where(AIJob.user_id == current_user.id, AIJob.status == "success")
            .order_by(AIJob.completed_at.desc())
        )
        .scalars()
        .first()
    )
    if job is None:
        raise JobNotFoundError("Belum ada job generate yang selesai untuk dijadikan project.")
    return job.id


def _run(db: Session, current_user: User, arguments: dict) -> dict:
    job_id = _resolve_job_id(db, current_user, arguments.get("job_id"))
    title = arguments.get("title") or "Video baru"
    mode = arguments.get("mode") or "product_ad"

    project = create_project_from_job(db, current_user, title, mode, job_id)
    return {"project_id": str(project.id), "status": project.status}


TOOL = AgentTool(
    spec=ToolSpec(
        name="create_project_tool",
        description=(
            "Buat project editor dari job generate yang sudah sukses (default: job "
            "sukses paling baru kalau job_id tidak disebut)."
        ),
        parameters={
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "string",
                    "description": "ID job generate yang sudah sukses (opsional).",
                },
                "title": {"type": "string", "description": "Judul project."},
                "mode": {
                    "type": "string",
                    "enum": ["product_ad", "affiliate"],
                    "description": "Framing konten: iklan produk atau affiliate.",
                },
            },
        },
    ),
    run=_run,
)
