"""Wraps `generation_service.create_generate_video_job` — the same path
`POST /ai/generate-video` uses. Resolves the source photo via
`select_media_tool.resolve_media_asset` (defaults to the user's most recently
uploaded photo) so a single turn like "generate video dari foto ini" works without the
LLM needing to call `select_media_tool` first.
"""
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.agent_tools.base import AgentTool
from app.services.agent_tools.select_media_tool import resolve_media_asset
from app.services.generation_service import create_generate_video_job
from app.services.llm_providers.base import ToolSpec


def _run(db: Session, current_user: User, arguments: dict) -> dict:
    asset = resolve_media_asset(db, current_user, arguments.get("media_asset_id"))
    prompt = arguments.get("prompt")

    job = create_generate_video_job(db, current_user, asset.id, prompt)
    return {"job_id": str(job.id), "status": job.status, "result_url": job.result_url}


TOOL = AgentTool(
    spec=ToolSpec(
        name="generate_video_tool",
        description=(
            "Generate video AI dari foto (default: foto terbaru yang diupload user "
            "kalau media_asset_id tidak disebut). Memakai kuota AI generation user, "
            "dicek dulu sebelum jalan."
        ),
        parameters={
            "type": "object",
            "properties": {
                "media_asset_id": {
                    "type": "string",
                    "description": "ID foto sumber (opsional; default foto terbaru).",
                },
                "prompt": {
                    "type": "string",
                    "description": "Gaya referensi opsional untuk video yang di-generate.",
                },
            },
        },
    ),
    run=_run,
)
