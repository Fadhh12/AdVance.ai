"""Looks up a `Template` by id — pure read, no mutation, no Celery task. Returns the
preset prompt/mode for the frontend (or, via chat, the agent) to feed into
`generate_video_tool`/`create_project_tool` next.
"""
import uuid

from sqlalchemy.orm import Session

from app.models.template import Template
from app.models.user import User
from app.services.agent_tools.base import AgentTool
from app.services.errors import TemplateNotFoundError
from app.services.llm_providers.base import ToolSpec


def _run(db: Session, current_user: User, arguments: dict) -> dict:
    del current_user  # global catalog, not per-user
    template_id = arguments.get("template_id")
    template = db.get(Template, uuid.UUID(template_id)) if template_id else None
    if template is None or not template.is_active:
        raise TemplateNotFoundError("Template tidak ditemukan.")

    return {"prompt_preset": template.prompt_preset, "mode": template.mode}


TOOL = AgentTool(
    spec=ToolSpec(
        name="apply_template_tool",
        description="Ambil preset gaya (prompt + mode) dari template gallery.",
        parameters={
            "type": "object",
            "properties": {"template_id": {"type": "string", "description": "ID template."}},
            "required": ["template_id"],
        },
    ),
    run=_run,
)
