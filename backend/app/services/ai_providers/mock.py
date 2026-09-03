"""Default provider while no real image-to-video vendor is chosen (CLAUDE.md: don't
hardcode a provider without confirmation — see docs/research/ai-providers-comparison.md).
Lets the whole generate → job-status → (eventually) editor pipeline be exercised
end-to-end without an API key. **Does not produce an actual generated video** — it
echoes the source image URL back as `result_url` so downstream code has *something* to
point at; replace with a real provider (runway.py, kling.py, ...) before shipping.
"""
from app.services.ai_providers.base import VideoGenerationProvider, VideoGenerationResult


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

        return VideoGenerationResult(
            success=True,
            result_url=source_image_url,
            provider_job_id="mock-job",
        )
