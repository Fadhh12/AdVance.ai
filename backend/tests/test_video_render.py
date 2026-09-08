import pytest

from app.services import video_render


def test_trim_video_raises_actionable_error_when_ffmpeg_missing(monkeypatch):
    monkeypatch.setattr(video_render.shutil, "which", lambda _name: None)

    with pytest.raises(video_render.FFmpegNotAvailableError) as exc_info:
        video_render.trim_video("http://example.com/source.mp4", 0, 5)

    assert "ffmpeg" in str(exc_info.value).lower()


def test_mux_voiceover_raises_actionable_error_when_ffmpeg_missing(monkeypatch):
    monkeypatch.setattr(video_render.shutil, "which", lambda _name: None)

    with pytest.raises(video_render.FFmpegNotAvailableError) as exc_info:
        video_render.mux_voiceover(b"fake-video", b"fake-audio")

    assert "ffmpeg" in str(exc_info.value).lower()


def test_mux_voiceover_replaces_audio_track_with_real_ffmpeg():
    """Real ffmpeg run (no monkeypatching) — builds a tiny silent video and a tiny
    audio tone via lavfi sources, then asserts mux_voiceover produces a playable clip
    whose length follows the (longer) audio, per its own docstring."""
    import shutil
    import subprocess
    import tempfile
    from pathlib import Path

    if not shutil.which("ffmpeg"):
        pytest.skip("ffmpeg not installed on this machine")

    with tempfile.TemporaryDirectory() as tmp_dir:
        video_path = Path(tmp_dir) / "video.mp4"
        audio_path = Path(tmp_dir) / "audio.mp3"

        # 1s video, 3s audio — output should end up ~3s (video frame frozen to cover
        # the gap), not cut off at 1s.
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=64x64:d=1",
                str(video_path),
            ],
            capture_output=True, check=True,
        )
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                "-t", "3", str(audio_path),
            ],
            capture_output=True, check=True,
        )

        output_bytes = video_render.mux_voiceover(
            video_path.read_bytes(), audio_path.read_bytes()
        )

        output_path = Path(tmp_dir) / "output.mp4"
        output_path.write_bytes(output_bytes)
        probe = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(output_path),
            ],
            capture_output=True, text=True, check=True,
        )
        duration = float(probe.stdout.strip())
        assert duration >= 2.5  # matches the 3s audio, not the 1s source video
