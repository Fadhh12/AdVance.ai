"""The "editorial-newspaper" motion preset — paper-cutout/newspaper collage energy:
punch zoom on emphasis beats, a fast pan standing in for whip pan, snap cuts, one
frame-flash transition, handheld micro-shake, optional caption burn-in. Vertical 9:16,
5-7 seconds. Spec supplied by the user (two prompts: a Google-Omni-style TikTok
reference and explicit "build this as a preset" instructions) — this module is the
ffmpeg-only implementation of that spec (no paid AI video-gen provider involved).

Approach: rather than one large `filter_complex` graph (fragile to get exactly right,
hard to debug), this builds 3 short single-image Ken-Burns clips from 3 stills pulled
out of the source at different timestamps (reusing the same proven zoompan technique as
`video_render.synthesize_placeholder_video`, just with punchier per-shot expressions),
plus one tiny flash clip, then concatenates them with ffmpeg's concat demuxer. Simple,
debuggable, each ffmpeg call has exactly one job.
"""
import subprocess
from pathlib import Path

from app.services.motion_presets.base import MotionPresetSpec
from app.services.video_render import run_ffmpeg

# Bundled directly (rather than relying on the OS's font/fontconfig setup) — the
# Windows ffmpeg build used in dev has no fontconfig config file at all, so a
# family-name lookup fails outright; a real `fontfile` path works identically on
# Windows/Linux/CI. Anton (OFL-licensed, see assets/OFL.txt) — a condensed bold
# display face, fits the "editorial newspaper headline" look this preset is going for.
_FONT_PATH = Path(__file__).parent / "assets" / "Anton-Regular.ttf"

SPEC = MotionPresetSpec(
    id="editorial-newspaper",
    name="Editorial Newspaper",
    description=(
        "Gaya paper-cutout/newspaper collage: punch zoom di momen penting, pan cepat "
        "ala whip pan, snap cut, frame flash, handheld micro-shake. Vertikal 9:16, "
        "5-7 detik — cocok untuk hook TikTok/Reels yang agresif."
    ),
    aspect_ratio="9:16",
    min_duration_seconds=5.0,
    max_duration_seconds=7.0,
)

_WIDTH = 1080
_HEIGHT = 1920
_FPS = 30
_FLASH_SECONDS = 0.08

# (zoom expr, x expr, y expr) per shot — `zoom`/`on` are zoompan's own variables
# (current zoom factor, output frame index). Centered zoompan formula
# (iw/2-(iw/zoom/2)) matches standard Ken Burns centering; shot 2/3 add a drift/shake
# term on top of it for the pan + handheld feel.
_SHOT_EXPRESSIONS = [
    # Shot 1: aggressive punch zoom in, held center — the "hook" beat.
    ("min(zoom+0.05,1.7)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    # Shot 2: zoom out fast + horizontal drift (whip-pan stand-in).
    (
        "if(lte(on,1),1.6,max(1.05,zoom-0.035))",
        "iw/2-(iw/zoom/2)+140*sin(on/3)",
        "ih/2-(ih/zoom/2)",
    ),
    # Shot 3: gentle punch-in with handheld micro-shake jitter.
    (
        "min(zoom+0.018,1.3)",
        "iw/2-(iw/zoom/2)+5*sin(on*1.3)",
        "ih/2-(ih/zoom/2)+5*cos(on*1.1)",
    ),
]


def _probe_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    try:
        duration = float(result.stdout.strip())
        return duration if duration > 0 else 4.0
    except ValueError:
        return 4.0  # falls back to the known duration of the mock provider's clip


def _extract_frame(source_path: Path, timestamp: float, output_path: Path) -> None:
    run_ffmpeg(
        ["ffmpeg", "-y", "-ss", str(max(0.0, timestamp)), "-i", str(source_path),
         "-vframes", "1", str(output_path)]
    )


def _render_shot(
    frame_path: Path,
    output_path: Path,
    duration: float,
    zoom_expr: str,
    x_expr: str,
    y_expr: str,
) -> None:
    frame_count = max(1, round(duration * _FPS))
    run_ffmpeg([
        "ffmpeg", "-y", "-loop", "1", "-i", str(frame_path), "-t", str(duration),
        "-vf",
        # Pre-scale to 2x the output canvas so zoompan has headroom to punch in
        # without hitting the source edges or upscaling visibly.
        f"scale={_WIDTH * 2}:{_HEIGHT * 2}:force_original_aspect_ratio=increase,"
        f"crop={_WIDTH * 2}:{_HEIGHT * 2},"
        f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':"
        f"d={frame_count}:s={_WIDTH}x{_HEIGHT}:fps={_FPS}",
        "-pix_fmt", "yuv420p", "-c:v", "libx264",
        str(output_path),
    ])


def _render_flash(output_path: Path) -> None:
    run_ffmpeg([
        "ffmpeg", "-y", "-f", "lavfi", "-i",
        f"color=c=white:s={_WIDTH}x{_HEIGHT}:d={_FLASH_SECONDS}:r={_FPS}",
        "-pix_fmt", "yuv420p", "-c:v", "libx264",
        str(output_path),
    ])


def _escape_drawtext(caption: str) -> str:
    # `expansion=none` is set on the filter itself (see `build()`), so '%' needs no
    # special handling — without it, drawtext's default expand-mode treats a bare '%'
    # as the start of a format specifier and errors ("Stray %") on anything else,
    # confirmed against a real ffmpeg run. Still need to escape ':' (filter option
    # separator) and swap the unescapable single quote for a visual lookalike.
    return caption.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’")


def _escape_filter_path(path: Path) -> str:
    # ffmpeg filter option values split on ':' — an unescaped Windows drive letter
    # ("C:/...") breaks parsing, so the colon needs its own backslash escape.
    return path.resolve().as_posix().replace(":", "\\:")


def build(source_path: Path, work_dir: Path, caption: str | None, total_duration: float) -> Path:
    """Builds the styled clip from `source_path` (a video, per the pipeline's current
    convention — see `video_render.trim_video`), writes intermediate files under
    `work_dir`, and returns the final output path.
    """
    source_duration = _probe_duration(source_path)
    shot_duration = max(0.6, (total_duration - _FLASH_SECONDS) / 3)

    # Spread the 3 "shots" across whatever footage exists — if the source is very
    # short (e.g. the mock provider's 4s placeholder), timestamps just land close
    # together, which is fine: each shot re-derives its look from zoompan, not from
    # the source frame differing much.
    timestamps = [
        min(0.15, source_duration * 0.05),
        source_duration / 2,
        max(0.0, source_duration - 0.2),
    ]

    shot_paths: list[Path] = []
    for index, (timestamp, (zoom_expr, x_expr, y_expr)) in enumerate(
        zip(timestamps, _SHOT_EXPRESSIONS)
    ):
        frame_path = work_dir / f"shot_{index}_frame.jpg"
        shot_path = work_dir / f"shot_{index}.mp4"
        _extract_frame(source_path, timestamp, frame_path)
        _render_shot(frame_path, shot_path, shot_duration, zoom_expr, x_expr, y_expr)
        shot_paths.append(shot_path)

    flash_path = work_dir / "flash.mp4"
    _render_flash(flash_path)

    # Snap cut shot0->shot1 (straight concat), frame-flash shot1->shot2 (a beat of
    # pure white spliced in — "frame flash transition").
    concat_list_path = work_dir / "concat.txt"
    concat_entries = [shot_paths[0], shot_paths[1], flash_path, shot_paths[2]]
    concat_list_path.write_text(
        "\n".join(f"file '{path.resolve().as_posix()}'" for path in concat_entries)
    )

    concatenated_path = work_dir / "concatenated.mp4"
    run_ffmpeg([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list_path),
        "-c", "copy", str(concatenated_path),
    ])

    if not caption:
        return concatenated_path

    captioned_path = work_dir / "captioned.mp4"
    run_ffmpeg([
        "ffmpeg", "-y", "-i", str(concatenated_path),
        "-vf",
        f"drawtext=fontfile='{_escape_filter_path(_FONT_PATH)}':"
        f"text='{_escape_drawtext(caption)}':expansion=none:fontcolor=white:fontsize=64:"
        "box=1:boxcolor=black@0.6:boxborderw=20:x=(w-text_w)/2:y=h-320",
        "-pix_fmt", "yuv420p", "-c:v", "libx264",
        str(captioned_path),
    ])
    return captioned_path
