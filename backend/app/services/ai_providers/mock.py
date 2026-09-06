"""Default provider while no real image-to-video vendor is chosen (CLAUDE.md: don't
hardcode a provider without confirmation — see docs/research/ai-providers-comparison.md).
Lets the whole generate → job-status → editor pipeline be exercised end-to-end without
an API key. **Does not produce an actual AI-generated video** — where ffmpeg is
available it turns the source photo into a short real MP4 clip (see
`synthesize_placeholder_video`) purely so the rest of the pipeline (trim/export/preview)
has a genuine playable video to work with instead of a raw image link; replace this
whole provider with a real one (runway.py, kling.py, ...) before shipping.
"""
import io
import logging
import uuid

from app.services.ai_providers.base import VideoGenerationProvider, VideoGenerationResult
from app.services.storage import generate_presigned_url, upload_object
from app.services.video_render import synthesize_placeholder_video

logger = logging.getLogger(__name__)


class MockVideoProvider(VideoGenerationProvider):
    def generate_video(
        self, source_image_url: str, prompt: str | None = None
    ) -> VideoGenerationResult:
        # Test hook: a caller can force the failure path without needing a real
        # provider error condition (see tests/test_ai.py).
        if prompt and "trigger-failure" in prompt:
            return VideoGenerationResult(
                success=False, error_message="Simulated provider failure (mock)."
            )

        try:
            video_bytes = synthesize_placeholder_video(source_image_url)
            key = f"mock-generated/{uuid.uuid4()}.mp4"
            upload_object(key, io.BytesIO(video_bytes), "video/mp4")
            result_url = generate_presigned_url(key)
        except Exception as exc:  # noqa: BLE001 — intentional: ffmpeg/network/decode
            # failures here must not fail generation. No ffmpeg on PATH (e.g. CI, per
            # PROGRESS.md), or the "photo" isn't a real decodable image (e.g. test
            # fixtures use fake bytes) — fall back to the old echo behavior instead.
            logger.warning("MockVideoProvider: placeholder video synthesis skipped: %s", exc)
            result_url = source_image_url

        return VideoGenerationResult(
            success=True,
            result_url=result_url,
            provider_job_id="mock-job",
        )
