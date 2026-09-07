"""Phase 6R-8 — motion preset catalog endpoint, engine dispatch, and the render task's
preset-vs-trim branch. Real ffmpeg filter-graph correctness (zoompan/concat/drawtext
actually producing a good-looking clip) is verified manually against a real ffmpeg
install per PROGRESS.md, not here — these tests cover the dispatch/error contracts that
must hold regardless of the machine.
"""
import pytest
from moto import mock_aws

import app.workers.tasks as tasks_module
from app.core.config import get_settings
from app.services import video_render
from app.services.errors import InvalidMotionPresetError
from app.services.motion_presets.engine import apply_motion_preset
from app.services.storage import get_s3_client


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


def _auth_headers(client, email="motion@example.com") -> dict:
    response = client.post(
        "/auth/register", json={"email": email, "password": "hunter22", "name": "Nabil"}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _successful_job_id(client, headers, s3_bucket) -> str:
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


def test_list_motion_presets_includes_editorial_newspaper(client):
    headers = _auth_headers(client)
    response = client.get("/motion-presets", headers=headers)
    assert response.status_code == 200
    ids = {preset["id"] for preset in response.json()}
    assert "editorial-newspaper" in ids


def test_list_motion_presets_requires_auth(client):
    response = client.get("/motion-presets")
    assert response.status_code == 401


def test_apply_motion_preset_rejects_unknown_id():
    with pytest.raises(InvalidMotionPresetError):
        apply_motion_preset("not-a-real-preset", "http://example.com/source.mp4")


def test_apply_motion_preset_fails_loud_without_ffmpeg(monkeypatch):
    monkeypatch.setattr(video_render.shutil, "which", lambda _name: None)

    with pytest.raises(video_render.FFmpegNotAvailableError):
        apply_motion_preset("editorial-newspaper", "http://example.com/source.mp4")


def test_render_with_motion_preset_uses_preset_engine_not_trim(client, s3_bucket, monkeypatch):
    calls = {"preset": None, "trim_called": False}

    def fake_apply_motion_preset(preset_id, source_url, caption=None):
        calls["preset"] = preset_id
        return b"fake-mp4-bytes"

    def fake_trim_video(*args, **kwargs):
        calls["trim_called"] = True
        return b"should-not-be-called"

    monkeypatch.setattr(tasks_module, "apply_motion_preset", fake_apply_motion_preset)
    monkeypatch.setattr(tasks_module, "trim_video", fake_trim_video)

    headers = _auth_headers(client)
    job_id = _successful_job_id(client, headers, s3_bucket)
    project = client.post(
        "/projects",
        json={"title": "Iklan sepatu", "mode": "product_ad", "source_job_id": job_id},
        headers=headers,
    ).json()

    client.patch(
        f"/projects/{project['id']}",
        json={"motion_preset": "editorial-newspaper"},
        headers=headers,
    )

    response = client.post(f"/projects/{project['id']}/render", headers=headers)
    assert response.status_code == 202
    body = response.json()
    assert body["render_status"] == "success"
    assert body["motion_preset"] == "editorial-newspaper"
    assert calls["preset"] == "editorial-newspaper"
    assert calls["trim_called"] is False
