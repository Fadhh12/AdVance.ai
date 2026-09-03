"""Voice-over/TTS interface (optional per project, per Task Breakdown Phase 3). Not
wired to an endpoint yet — provider choice not finalized (see
docs/research/ai-providers-comparison.md: ElevenLabs vs Google/Azure TTS).
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class VoiceoverResult:
    success: bool
    audio_url: str | None = None
    error_message: str | None = None


class VoiceoverProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, voice: str | None = None) -> VoiceoverResult:
        raise NotImplementedError
