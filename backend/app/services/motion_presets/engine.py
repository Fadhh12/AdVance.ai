"""Public entrypoint for the motion preset engine — same shape/contract as
`video_render.export_for_platform`: downloads the source, works in a temp dir, returns
raw bytes, never touches storage directly (the caller uploads).
"""
import tempfile
from pathlib import Path

from app.services.errors import InvalidMotionPresetError
from app.services.motion_presets.registry import MOTION_PRESETS, get_builder
from app.services.video_render import download_file, ensure_ffmpeg_available


def apply_motion_preset(preset_id: str, source_url: str, caption: str | None = None) -> bytes:
    spec = MOTION_PRESETS.get(preset_id)
    builder = get_builder(preset_id)
    if spec is None or builder is None:
        raise InvalidMotionPresetError(f"Motion preset {preset_id!r} tidak dikenal.")

    ensure_ffmpeg_available()

    with tempfile.TemporaryDirectory() as tmp_dir:
        work_dir = Path(tmp_dir)
        source_path = work_dir / "source.mp4"
        download_file(source_url, source_path)

        target_duration = (spec.min_duration_seconds + spec.max_duration_seconds) / 2
        output_path = builder(source_path, work_dir, caption, target_duration)
        return output_path.read_bytes()
