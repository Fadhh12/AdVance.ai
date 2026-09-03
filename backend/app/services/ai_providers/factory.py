"""Picks the configured provider (`AI_VIDEO_PROVIDER` in .env) — the only place in the
codebase that's allowed to know provider names. Everything else talks to
`VideoGenerationProvider`.
"""
from app.core.config import get_settings
from app.services.ai_providers.base import VideoGenerationProvider
from app.services.ai_providers.mock import MockVideoProvider


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
