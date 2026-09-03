"""Abstract interface every AI video-generation provider wrapper must implement.

CLAUDE.md: provider AI belum final dipilih — jangan hardcode ke satu provider tanpa
konfirmasi user. Semua kode di luar `services/ai_providers/` bicara ke provider lewat
interface ini saja, supaya ganti provider = tambah 1 file baru, bukan ubah kode lain.

Diisi konkret di Phase 3. Filled in here (Phase 0) so the folder isn't empty and the
contract is settled before any provider-specific code is written.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


class TransientProviderError(Exception):
    """Raise this (not a bare Exception) for retryable failures — network blip, provider
    rate limit, timeout. The Celery task auto-retries up to 3x with backoff on this
    (SRS §2.3). Anything else raised is treated as a bug, not a retryable condition.
    A *non*-retryable provider failure (bad input, content policy, etc.) is not an
    exception at all — return `VideoGenerationResult(success=False, error_message=...)`.
    """


@dataclass
class VideoGenerationResult:
    success: bool
    result_url: str | None = None
    error_message: str | None = None
    provider_job_id: str | None = None


class VideoGenerationProvider(ABC):
    """One implementation per provider (e.g. runway.py, kling.py). Never call a provider's
    SDK/HTTP API directly from routers or Celery tasks — always go through this interface.
    """

    @abstractmethod
    def generate_video(
        self, source_image_url: str, prompt: str | None = None
    ) -> VideoGenerationResult:
        """Kick off (or synchronously perform, if the worker handles polling) image-to-video
        generation. Raise `TransientProviderError` for retryable failures; a permanent
        failure (bad input, content policy, ...) comes back as
        `VideoGenerationResult(success=False, error_message=...)` instead.
        """
        raise NotImplementedError
