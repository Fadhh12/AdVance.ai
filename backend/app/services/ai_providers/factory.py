"""Picks the configured provider (`AI_VIDEO_PROVIDER`/`AI_IMAGE_PROVIDER`/
`AI_VOICEOVER_PROVIDER` in .env) — the only place in the codebase that's allowed to
know provider names. Everything else talks to the abstract interfaces
(`VideoGenerationProvider`, `ImageGenerationProvider`, `VoiceoverProvider`).
"""
from app.core.config import get_settings
from app.services.ai_providers.base import VideoGenerationProvider
from app.services.ai_providers.image import ImageGenerationProvider
from app.services.ai_providers.mock import MockVideoProvider
from app.services.ai_providers.mock_image import MockImageProvider
from app.services.ai_providers.mock_voiceover import MockVoiceoverProvider
from app.services.ai_providers.voiceover import VoiceoverProvider


def get_video_provider() -> VideoGenerationProvider:
    provider_name = get_settings().ai_video_provider
    if provider_name == "mock":
        return MockVideoProvider()

    # Real providers (Runway, Kling, ...) land here once one is confirmed — see
    # docs/research/ai-providers-comparison.md. Fail loud rather than silently
    # falling back to mock if someone sets an unimplemented name in .env.
    raise NotImplementedError(
        f"AI_VIDEO_PROVIDER={provider_name!r} belum diimplementasi. "
        "Provider yang tersedia sekarang: 'mock'."
    )


def get_image_provider() -> ImageGenerationProvider:
    """AI Image skill (Phase 6R) — no real provider chosen yet, same rule as video."""
    provider_name = get_settings().ai_image_provider
    if provider_name == "mock":
        return MockImageProvider()

    raise NotImplementedError(
        f"AI_IMAGE_PROVIDER={provider_name!r} belum diimplementasi. "
        "Provider yang tersedia sekarang: 'mock'."
    )


def get_voiceover_provider() -> VoiceoverProvider:
    """AI Audio skill. Default real provider (Phase 6R-9): `edge_tts` — free, no API
    key, same "free provider first" call as the LLM factory's Gemini default. Lazy
    import so the `edge-tts` dependency isn't required while still on 'mock'.
    """
    provider_name = get_settings().ai_voiceover_provider
    if provider_name == "mock":
        return MockVoiceoverProvider()
    if provider_name == "edge_tts":
        from app.services.ai_providers.edge_tts_voiceover import EdgeTTSVoiceoverProvider

        return EdgeTTSVoiceoverProvider()

    raise NotImplementedError(
        f"AI_VOICEOVER_PROVIDER={provider_name!r} belum diimplementasi. "
        "Provider yang tersedia sekarang: 'mock', 'edge_tts'."
    )
