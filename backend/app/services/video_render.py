"""Ffmpeg-backed video processing: trim (editor, FR-05) and per-platform export (Publish
Manual Assist, FR-13/SRS §2.2). Requires the `ffmpeg` binary on PATH — not bundled by
pip. **Not installed on the primary dev machine as of Phase 4** (see PROGRESS.md) — this
is written correctly against a real install and fails loud with an actionable message
when the binary is missing, rather than silently no-op'ing.
"""
import shutil
import subprocess
import tempfile
from pathlib import Path

import httpx

# SRS §2.2: IG Reels <=90s, TikTok <=10min, YouTube Shorts <=60s.
PLATFORM_DURATION_LIMITS_SECONDS = {
    "instagram": 90,
    "tiktok": 600,
    "youtube": 60,
}


class FFmpegNotAvailableError(Exception):
    pass


class VideoRenderError(Exception):
    pass


def ensure_ffmpeg_available() -> None:
    if shutil.which("ffmpeg") is None:
        raise FFmpegNotAvailableError(
            "ffmpeg tidak ditemukan di PATH. Install ffmpeg dulu, lalu render ulang "
            "(lihat backend/README.md)."
        )


def download_file(source_url: str, destination: Path) -> None:
    with httpx.stream("GET", source_url, timeout=60) as response:
        response.raise_for_status()
        with open(destination, "wb") as f:
            for chunk in response.iter_bytes():
                f.write(chunk)


def run_ffmpeg(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise VideoRenderError(f"ffmpeg gagal: {result.stderr[-500:]}")


def trim_video(
    source_url: str, start_seconds: float | None, end_seconds: float | None
) -> bytes:
    """Downloads `source_url`, trims to [start_seconds, end_seconds), returns the
    result's raw MP4 bytes. Caller uploads them to storage — this module never touches
    S3 directly, keeping it testable in isolation.
    """
    ensure_ffmpeg_available()

    with tempfile.TemporaryDirectory() as tmp_dir:
        source_path = Path(tmp_dir) / "source.mp4"
        output_path = Path(tmp_dir) / "trimmed.mp4"
        download_file(source_url, source_path)

        command = ["ffmpeg", "-y", "-i", str(source_path)]
        if start_seconds is not None:
            command += ["-ss", str(start_seconds)]
        if end_seconds is not None:
            command += ["-to", str(end_seconds)]
        command += [str(output_path)]

        run_ffmpeg(command)
        return output_path.read_bytes()


def synthesize_placeholder_video(image_url: str, duration_seconds: float = 4.0) -> bytes:
    """Turns a still photo into a short silent MP4 clip via ffmpeg (loop + pan/zoom),
    portrait-framed to match the platform export target (1080x1920).

    This is **not** AI video generation — it exists only so `MockVideoProvider`
    (services/ai_providers/mock.py) hands the rest of the pipeline a real, playable
    video instead of literally the source photo URL. Without this, `trim_video`/
    `export_for_platform` downstream ffmpeg calls a 1-frame near-zero-duration input,
    which reads as a frozen/"stuck" video in the editor preview. Delete this the moment
    a real image-to-video provider (Runway/Kling/...) is wired in — see
    docs/research/ai-providers-comparison.md and CLAUDE.md on not hardcoding a provider.
    """
    ensure_ffmpeg_available()

    with tempfile.TemporaryDirectory() as tmp_dir:
        image_path = Path(tmp_dir) / "source"
        output_path = Path(tmp_dir) / "placeholder.mp4"
        download_file(image_url, image_path)

        frame_count = max(1, round(duration_seconds * 25))
        command = [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(image_path),
            "-t",
            str(duration_seconds),
            "-vf",
            # Slow zoom-in ("Ken Burns") so it visibly plays rather than sitting on a
            # static frame — still framed 9:16 to match the platform export target.
            f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"zoompan=z='min(zoom+0.0008,1.15)':d={frame_count}:s=1080x1920:fps=25",
            "-pix_fmt",
            "yuv420p",
            "-c:v",
            "libx264",
            str(output_path),
        ]

        run_ffmpeg(command)
        return output_path.read_bytes()


def export_for_platform(source_url: str, platform: str) -> bytes:
    """Crops to 9:16 (center crop after fill-scale to 1080x1920) and caps duration to
    the platform's limit (SRS §2.2) — auto-adjust rather than just rejecting an
    oversized/wrong-ratio video. Unknown `platform` is a programmer error, not a user
    one — validate against `PLATFORM_DURATION_LIMITS_SECONDS` before calling this.
    """
    duration_limit = PLATFORM_DURATION_LIMITS_SECONDS[platform]
    ensure_ffmpeg_available()

    with tempfile.TemporaryDirectory() as tmp_dir:
        source_path = Path(tmp_dir) / "source.mp4"
        output_path = Path(tmp_dir) / f"{platform}.mp4"
        download_file(source_url, source_path)

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(source_path),
            "-t",
            str(duration_limit),
            "-vf",
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            str(output_path),
        ]

        run_ffmpeg(command)
        return output_path.read_bytes()
