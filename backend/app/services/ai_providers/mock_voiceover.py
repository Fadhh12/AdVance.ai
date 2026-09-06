"""Default voiceover provider while no real TTS one is chosen (see `voiceover.py` —
interface existed as an unwired stub since Phase 0; this is the first concrete
implementation, wired up in Phase 6R as the AI agent's "AI Audio" skill). Real speech
synthesis needs an actual TTS engine — this mock can't produce real speech, so it
generates a silent placeholder clip of a plausible spoken-length duration via ffmpeg,
clearly not real audio. Swap for a real provider (ElevenLabs, Google/Azure TTS, ...)
before shipping — see docs/research/ai-providers-comparison.md.
"""
import io
import subprocess
import tempfile
import uuid
from pathlib import Path

from app.services.ai_providers.voiceover import VoiceoverProvider, VoiceoverResult
from app.services.storage import upload_object
from app.services.video_render import FFmpegNotAvailableError, ensure_ffmpeg_available

_WORDS_PER_SECOND = 2.5  # rough average speaking pace, just to size the placeholder
_MIN_SECONDS = 1.0
_MAX_SECONDS = 30.0


class MockVoiceoverProvider(VoiceoverProvider):
    def synthesize(self, text: str, voice: str | None = None) -> VoiceoverResult:
        del voice  # mock has no real voices to pick from
        try:
            ensure_ffmpeg_available()
        except FFmpegNotAvailableError as exc:
            return VoiceoverResult(success=False, error_message=str(exc))

        word_count = max(1, len(text.split()))
        duration = min(_MAX_SECONDS, max(_MIN_SECONDS, word_count / _WORDS_PER_SECOND))

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "voiceover.mp3"
            command = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                "-t", str(duration),
                str(output_path),
            ]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                return VoiceoverResult(
                    success=False, error_message=f"ffmpeg gagal: {result.stderr[-500:]}"
                )
            audio_bytes = output_path.read_bytes()

        key = f"mock-generated/{uuid.uuid4()}.mp3"
        upload_object(key, io.BytesIO(audio_bytes), "audio/mpeg")
        return VoiceoverResult(success=True, audio_key=key)
