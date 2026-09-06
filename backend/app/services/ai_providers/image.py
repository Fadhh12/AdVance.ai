"""Abstract interface every AI image-generation provider wrapper must implement
(Phase 6R — "AI Image" skill, requested to match the Dreamina reference). No real
provider chosen yet (same CLAUDE.md rule as video/TTS) — abstracted here so a real one
(e.g. Gemini's image model, Stability, ...) is a new file, not a change anywhere else.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ImageGenerationResult:
    success: bool
    # Object storage **key** (not a signed URL) — unlike VideoGenerationResult, the
    # only consumer of this is a MediaAsset row (see generate_image_tool.py), which
    # already presigns file_url fresh on every read the same way an upload does.
    result_key: str | None = None
    error_message: str | None = None


class ImageGenerationProvider(ABC):
    """One implementation per provider. Never call a provider's SDK/HTTP API directly
    from routers, services, or Celery tasks — always go through this interface.
    """

    @abstractmethod
    def generate_image(self, prompt: str) -> ImageGenerationResult:
        raise NotImplementedError
