""""AI Audio" skill (Phase 6R, requested to match the Dreamina reference) — text to
speech via `app/services/ai_providers/voiceover.py`. No real TTS provider chosen yet;
the mock produces a real (silent, clearly placeholder) audio `MediaAsset` so the rest
of the pipeline — picking a voiceover track in the editor, later — has something real
to point at once that UI exists.
"""
import uuid as uuid_module

from sqlalchemy.orm import Session

from app.models.media_asset import MediaAsset
from app.models.user import User
from app.services.agent_tools.base import AgentTool
from app.services.ai_providers.factory import get_voiceover_provider
from app.services.errors import GenerationFailedError
from app.services.llm_providers.base import ToolSpec


def _run(db: Session, current_user: User, arguments: dict) -> dict:
    text = arguments.get("text", "").strip()
    if not text:
        raise GenerationFailedError("Butuh naskah/teks yang mau dijadikan voiceover.")

    result = get_voiceover_provider().synthesize(text, voice=arguments.get("voice"))
    if not result.success or not result.audio_key:
        raise GenerationFailedError(result.error_message or "Generate voiceover gagal.")

    asset = MediaAsset(
        user_id=current_user.id,
        type="audio",
        file_url=result.audio_key,
        original_filename=f"ai-voiceover-{uuid_module.uuid4().hex[:8]}.mp3",
        content_type="audio/mpeg",
        size_bytes=0,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    return {"media_asset_id": str(asset.id)}


TOOL = AgentTool(
    spec=ToolSpec(
        name="generate_voiceover_tool",
        description=(
            "Generate voiceover (text-to-speech) dari naskah teks (AI Audio). "
            "Hasilnya masuk ke Media Library sebagai file audio."
        ),
        parameters={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Naskah yang mau diucapkan."},
                "voice": {"type": "string", "description": "Nama suara (opsional)."},
            },
            "required": ["text"],
        },
    ),
    run=_run,
)
