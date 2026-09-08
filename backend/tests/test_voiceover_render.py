"""Phase 6R-13 — voice-over script (`ContentProject.voiceover_text`) gets synthesized
and muxed onto the rendered clip's audio track. Uses the real `MockVoiceoverProvider`
(forced by conftest's `_force_mock_providers`) + real ffmpeg, same "verify the
dispatch/error contract for real, leave frame-level correctness to manual check"
approach as test_motion_presets.py — the mock provider's silent placeholder clip is
real enough to mux and assert against, unlike stubbing bytes directly.
"""
import subprocess
import tempfile
from pathlib import Path

import pytest
from moto import mock_aws

import app.workers.tasks as tasks_module
from app.core.config import get_settings
from app.services.ai_providers.voiceover import VoiceoverResult
from app.services.storage import get_s3_client


def _fake_rendered_video_bytes() -> bytes:
    """A real, tiny, valid mp4 (not a dummy bytes literal) — trim_video is
    monkeypatched to return this instead of actually downloading+trimming the source
    job's video, because that download goes through `httpx` straight to a presigned
    URL rather than through boto3, which moto's `s3_bucket` fixture below doesn't
    intercept (test_motion_presets.py's dispatch tests sidestep the same gap by
    monkeypatching trim_video/apply_motion_preset too). The voiceover mux step right
    after this in render_project_task still runs real ffmpeg against real bytes.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        video_path = Path(tmp_dir) / "video.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=64x64:d=1", str(video_path)],
            capture_output=True,
            check=True,
        )
        return video_path.read_bytes()


@pytest.fixture()
def s3_bucket():
    settings = get_settings()
    original_endpoint = settings.s3_endpoint_url
    settings.s3_endpoint_url = None
    try:
        with mock_aws():
            get_s3_client().create_bucket(Bucket=settings.s3_bucket_name)
            yield
    finally:
        settings.s3_endpoint_url = original_endpoint


def _auth_headers(client, email="voiceover@example.com") -> dict:
    response = client.post(
        "/auth/register", json={"email": email, "password": "hunter22", "name": "Nabil"}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _successful_job_id(client, headers) -> str:
    upload = client.post(
        "/media/upload",
        files={"file": ("product.jpg", b"\xff\xd8\xff" + b"fake", "image/jpeg")},
        headers=headers,
    )
    asset_id = upload.json()["id"]
    job = client.post(
        "/ai/generate-video", json={"source_asset_id": asset_id}, headers=headers
    ).json()
    assert job["status"] == "success"
    return job["id"]


def test_render_with_voiceover_text_succeeds_and_muxes_audio(client, s3_bucket, monkeypatch):
    monkeypatch.setattr(
        tasks_module, "trim_video", lambda *args, **kwargs: _fake_rendered_video_bytes()
    )
    headers = _auth_headers(client)
    job_id = _successful_job_id(client, headers)
    project = client.post(
        "/projects",
        json={"title": "Iklan Oreo", "mode": "product_ad", "source_job_id": job_id},
        headers=headers,
    ).json()

    client.patch(
        f"/projects/{project['id']}",
        json={"voiceover_text": "Oreo dicelupkan ke susu, nikmat setiap gigitan."},
        headers=headers,
    )

    response = client.post(f"/projects/{project['id']}/render", headers=headers)
    assert response.status_code == 202
    body = response.json()
    assert body["render_status"] == "success"
    assert body["voiceover_text"] == "Oreo dicelupkan ke susu, nikmat setiap gigitan."
    assert body["final_video_url"] is not None


def test_render_marks_failed_when_voiceover_synthesis_fails(client, s3_bucket, monkeypatch):
    class FailingVoiceoverProvider:
        def synthesize(self, text, voice=None):
            return VoiceoverResult(success=False, error_message="TTS gagal (simulated).")

    monkeypatch.setattr(
        tasks_module, "get_voiceover_provider", lambda: FailingVoiceoverProvider()
    )
    monkeypatch.setattr(
        tasks_module, "trim_video", lambda *args, **kwargs: _fake_rendered_video_bytes()
    )

    headers = _auth_headers(client)
    job_id = _successful_job_id(client, headers)
    project = client.post(
        "/projects",
        json={"title": "Iklan Oreo", "mode": "product_ad", "source_job_id": job_id},
        headers=headers,
    ).json()

    client.patch(
        f"/projects/{project['id']}",
        json={"voiceover_text": "Naskah apa saja."},
        headers=headers,
    )

    response = client.post(f"/projects/{project['id']}/render", headers=headers)
    assert response.status_code == 202
    body = response.json()
    assert body["render_status"] == "failed"
    assert "TTS gagal" in body["render_error_message"]


def test_render_without_voiceover_text_skips_voiceover_step(client, s3_bucket, monkeypatch):
    called = {"synthesize": False}

    class SpyProvider:
        def synthesize(self, text, voice=None):
            called["synthesize"] = True
            return VoiceoverResult(success=True, audio_key="unused")

    monkeypatch.setattr(tasks_module, "get_voiceover_provider", lambda: SpyProvider())
    monkeypatch.setattr(
        tasks_module, "trim_video", lambda *args, **kwargs: _fake_rendered_video_bytes()
    )

    headers = _auth_headers(client)
    job_id = _successful_job_id(client, headers)
    project = client.post(
        "/projects",
        json={"title": "Iklan tanpa suara", "mode": "product_ad", "source_job_id": job_id},
        headers=headers,
    ).json()

    response = client.post(f"/projects/{project['id']}/render", headers=headers)
    assert response.status_code == 202
    assert response.json()["render_status"] == "success"
    assert called["synthesize"] is False
