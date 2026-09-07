"""Real TTS provider (Phase 6R-9) — Microsoft Edge's neural voices via the open-source
`edge-tts` package. Free, no API key/billing needed — same "free provider first"
reasoning already applied to the LLM provider (Gemini over paid Claude, see
PROGRESS.md). Default voice is Indonesian since the product's UI/copy is Indonesian;
callers can still pass any edge-tts voice name explicitly.
"""
import asyncio
import io
import uuid

import edge_tts

from app.services.ai_providers.voiceover import VoiceoverProvider, VoiceoverResult
from app.services.storage import upload_object

DEFAULT_VOICE = "id-ID-ArdiNeural"


async def _synthesize_bytes_async(text: str, voice: str) -> bytes:
    communicate = edge_tts.Communicate(text, voice)
    chunks = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            chunks.extend(chunk["data"])
    return bytes(chunks)


def _synthesize_bytes(text: str, voice: str) -> bytes:
    """Thin sync wrapper around the actual network call — kept as its own function so
    tests can monkeypatch just this (no real network calls in CI), same pattern as
    ffmpeg-absence monkeypatching elsewhere in this codebase.
    """
    return asyncio.run(_synthesize_bytes_async(text, voice))


class EdgeTTSVoiceoverProvider(VoiceoverProvider):
    def synthesize(self, text: str, voice: str | None = None) -> VoiceoverResult:
        try:
            audio_bytes = _synthesize_bytes(text, voice or DEFAULT_VOICE)
        except Exception as exc:  # edge-tts raises its own exception types over network
            return VoiceoverResult(success=False, error_message=f"TTS gagal: {exc}")

        if not audio_bytes:
            return VoiceoverResult(success=False, error_message="TTS tidak menghasilkan audio.")

        key = f"voiceover/{uuid.uuid4()}.mp3"
        upload_object(key, io.BytesIO(audio_bytes), "audio/mpeg")
        return VoiceoverResult(success=True, audio_key=key)
