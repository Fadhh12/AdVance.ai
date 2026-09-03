"""Ffmpeg-backed trim for the lightweight editor (FR-05). Requires the `ffmpeg` binary
on PATH — not bundled by pip. **Not installed on the primary dev machine as of Phase 4**
(see PROGRESS.md) — this is written correctly against a real install and fails loud with
an actionable message when the binary is missing, rather than silently no-op'ing.
"""
import shutil
import subprocess
import tempfile
from pathlib import Path

import httpx


class FFmpegNotAvailableError(Exception):
    pass


class VideoRenderError(Exception):
    pass


def _ensure_ffmpeg_available() -> None:
    if shutil.which("ffmpeg") is None:
        raise FFmpegNotAvailableError(
            "ffmpeg tidak ditemukan di PATH. Install ffmpeg dulu, lalu render ulang "
            "(lihat backend/README.md)."
        )


def trim_video(
    source_url: str, start_seconds: float | None, end_seconds: float | None
) -> bytes:
    """Downloads `source_url`, trims to [start_seconds, end_seconds), returns the
    result's raw MP4 bytes. Caller uploads them to storage — this module never touches
    S3 directly, keeping it testable in isolation.
    """
    _ensure_ffmpeg_available()

    with tempfile.TemporaryDirectory() as tmp_dir:
        source_path = Path(tmp_dir) / "source.mp4"
        output_path = Path(tmp_dir) / "trimmed.mp4"

        with httpx.stream("GET", source_url, timeout=60) as response:
            response.raise_for_status()
            with open(source_path, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)

        command = ["ffmpeg", "-y", "-i", str(source_path)]
        if start_seconds is not None:
            command += ["-ss", str(start_seconds)]
        if end_seconds is not None:
            command += ["-to", str(end_seconds)]
        command += [str(output_path)]

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise VideoRenderError(f"ffmpeg gagal: {result.stderr[-500:]}")

        return output_path.read_bytes()
