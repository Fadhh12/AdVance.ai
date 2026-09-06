""""AI Image" skill (Phase 6R, requested to match the Dreamina reference). No real
image-generation provider chosen yet (`app/services/ai_providers/image.py`) — the mock
still produces a real, usable (if clearly placeholder) `MediaAsset`, so a generated
image can immediately be picked as the source for `generate_video_tool` just like any
uploaded photo.
"""
import uuid as uuid_module

from sqlalchemy.orm import Session

from app.models.media_asset import MediaAsset
from app.models.user import User
from app.services.agent_tools.base import AgentTool
from app.services.ai_providers.factory import get_image_provider
from app.services.errors import GenerationFailedError
from app.services.llm_providers.base import ToolSpec


def _run(db: Session, current_user: User, arguments: dict) -> dict:
    prompt = arguments.get("prompt", "").strip()
    if not prompt:
        raise GenerationFailedError("Butuh deskripsi gambar yang mau dibuat.")

    result = get_image_provider().generate_image(prompt)
    if not result.success or not result.result_key:
        raise GenerationFailedError(result.error_message or "Generate gambar gagal.")

    asset = MediaAsset(
        user_id=current_user.id,
        type="photo",
        file_url=result.result_key,
        original_filename=f"ai-image-{uuid_module.uuid4().hex[:8]}.png",
        content_type="image/png",
        size_bytes=0,  # generated in-process, not read back to measure — cosmetic only
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    return {"media_asset_id": str(asset.id)}


TOOL = AgentTool(
    spec=ToolSpec(
        name="generate_image_tool",
        description=(
            "Generate gambar dari deskripsi teks (AI Image). Hasilnya masuk ke Media "
            "Library dan bisa langsung dipakai sebagai sumber untuk generate video."
        ),
        parameters={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Deskripsi gambar yang diinginkan."}
            },
            "required": ["prompt"],
        },
    ),
    run=_run,
)
