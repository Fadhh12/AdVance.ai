import pytest

from app.services import video_render


def test_trim_video_raises_actionable_error_when_ffmpeg_missing(monkeypatch):
    monkeypatch.setattr(video_render.shutil, "which", lambda _name: None)

    with pytest.raises(video_render.FFmpegNotAvailableError) as exc_info:
        video_render.trim_video("http://example.com/source.mp4", 0, 5)

    assert "ffmpeg" in str(exc_info.value).lower()
