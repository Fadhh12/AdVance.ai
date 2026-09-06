"""Voice-over/TTS interface (optional per project, per Task Breakdown Phase 3). Wired
up in Phase 6R as the AI agent's "AI Audio" skill (`generate_voiceover_tool.py`) — real
provider choice still not finalized (see docs/research/ai-providers-comparison.md:
ElevenLabs vs Google/Azure TTS), only `MockVoiceoverProvider` exists so far.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class VoiceoverResult:
    success: bool
    # Object storage **key** (not a signed URL) — the only consumer is a MediaAsset
    # row, which already presigns file_url fresh on every read, same as an upload.
    audio_key: str | None = None
    error_message: str | None = None


class VoiceoverProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, voice: str | None = None) -> VoiceoverResult:
        raise NotImplementedError
