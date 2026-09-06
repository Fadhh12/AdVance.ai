"""Resolves which uploaded photo the agent should act on next. An LLM tool call can't
carry file bytes — this tool never uploads anything itself, it only looks up an
already-uploaded `MediaAsset`. The frontend uploads via the real `POST /media/upload`
endpoint first, then passes the resulting id as chat context (see `app/api/chat.py`).
`resolve_media_asset` is also used directly by `generate_video_tool` so a turn like
"generate video dari foto ini" works in one tool call, without requiring the LLM to
call `select_media_tool` first.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.media_asset import MediaAsset
from app.models.user import User
from app.services.agent_tools.base import AgentTool
from app.services.errors import MediaNotFoundError
from app.services.llm_providers.base import ToolSpec


def resolve_media_asset(
    db: Session, current_user: User, media_asset_id: str | None
) -> MediaAsset:
    if media_asset_id is not None:
        asset = db.execute(
            select(MediaAsset).where(
                MediaAsset.id == uuid.UUID(media_asset_id),
                MediaAsset.user_id == current_user.id,
            )
        ).scalar_one_or_none()
    else:
        asset = (
            db.execute(
                select(MediaAsset)
                .where(MediaAsset.user_id == current_user.id, MediaAsset.type == "photo")
                .order_by(MediaAsset.uploaded_at.desc())
            )
            .scalars()
            .first()
        )

    if asset is None:
        raise MediaNotFoundError("Belum ada foto yang bisa dipakai — upload dulu.")
    return asset


def _run(db: Session, current_user: User, arguments: dict) -> dict:
    asset = resolve_media_asset(db, current_user, arguments.get("media_asset_id"))
    return {"media_asset_id": str(asset.id), "original_filename": asset.original_filename}


TOOL = AgentTool(
    spec=ToolSpec(
        name="select_media_tool",
        description=(
            "Pilih foto yang sudah diupload user untuk dipakai di langkah berikutnya. "
            "Tidak meng-upload apapun — hanya mereferensikan foto yang sudah ada."
        ),
        parameters={
            "type": "object",
            "properties": {
                "media_asset_id": {
                    "type": "string",
                    "description": "ID foto yang sudah diupload (opsional; default foto terbaru).",
                }
            },
        },
    ),
    run=_run,
)
