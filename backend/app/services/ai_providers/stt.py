"""Speech-to-text interface for auto-caption (FR-04). Not wired to an endpoint yet —
provider choice not finalized (see docs/research/ai-providers-comparison.md: Whisper,
hosted vs self-hosted). Real wiring lands in Phase 4, alongside the caption edit UI
that would actually use it.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TranscriptionResult:
    success: bool
    caption_text: str | None = None
    error_message: str | None = None


class SpeechToTextProvider(ABC):
    @abstractmethod
    def transcribe(self, video_url: str) -> TranscriptionResult:
        raise NotImplementedError
