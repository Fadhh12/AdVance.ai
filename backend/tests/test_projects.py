import pytest
from moto import mock_aws

import app.workers.tasks as tasks_module
from app.core.config import get_settings
from app.services import video_render
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


def _auth_headers(client, email="editor@example.com") -> dict:
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


def test_create_project_requires_successful_job(client, s3_bucket):
    headers = _auth_headers(client)
    job_id = _successful_job_id(client, headers, s3_bucket)

    response = client.post(
        "/projects",
        json={"title": "Iklan sepatu", "mode": "product_ad", "source_job_id": job_id},
        headers=headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "draft"
    assert body["source_video_url"]
    assert body["render_status"] is None


def test_create_project_rejects_unfinished_job(client, s3_bucket):
    headers = _auth_headers(client)
    asset = client.post(
        "/media/upload",
        files={"file": ("product.jpg", b"\xff\xd8\xff" + b"fake", "image/jpeg")},
        headers=headers,
    ).json()
    failed_job = client.post(
        "/ai/generate-video",
        json={"source_asset_id": asset["id"], "prompt": "trigger-failure"},
        headers=headers,
    ).json()
    assert failed_job["status"] == "failed"

    response = client.post(
        "/projects",
        json={"title": "X", "mode": "affiliate", "source_job_id": failed_job["id"]},
        headers=headers,
    )
    assert response.status_code == 409


def test_patch_project_updates_edit_fields(client, s3_bucket):
    headers = _auth_headers(client)
    job_id = _successful_job_id(client, headers, s3_bucket)
    project = client.post(
        "/projects",
        json={"title": "Iklan sepatu", "mode": "product_ad", "source_job_id": job_id},
        headers=headers,
    ).json()

    response = client.patch(
        f"/projects/{project['id']}",
        json={"caption": "Sepatu lari terbaru!", "trim_start_seconds": 1.5, "trim_end_seconds": 8},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["caption"] == "Sepatu lari terbaru!"
    assert body["trim_start_seconds"] == 1.5
    assert body["trim_end_seconds"] == 8


def test_list_and_get_project_ownership(client, s3_bucket):
    headers_a = _auth_headers(client, email="owner@example.com")
    headers_b = _auth_headers(client, email="other@example.com")
    job_id = _successful_job_id(client, headers_a, s3_bucket)
    project = client.post(
        "/projects",
        json={"title": "Iklan sepatu", "mode": "product_ad", "source_job_id": job_id},
        headers=headers_a,
    ).json()

    own_list = client.get("/projects", headers=headers_a)
    assert len(own_list.json()) == 1

    other_list = client.get("/projects", headers=headers_b)
    assert other_list.json() == []

    forbidden = client.get(f"/projects/{project['id']}", headers=headers_b)
    assert forbidden.status_code == 404


def test_render_project_success_path(client, s3_bucket, monkeypatch):
    monkeypatch.setattr(tasks_module, "trim_video", lambda *args, **kwargs: b"fake-mp4-bytes")

    headers = _auth_headers(client)
    job_id = _successful_job_id(client, headers, s3_bucket)
    project = client.post(
        "/projects",
        json={"title": "Iklan sepatu", "mode": "product_ad", "source_job_id": job_id},
        headers=headers,
    ).json()

    response = client.post(f"/projects/{project['id']}/render", headers=headers)
    assert response.status_code == 202
    body = response.json()
    # Celery runs eagerly in tests (see conftest.py) — render already finished.
    assert body["render_status"] == "success"
    assert body["final_video_url"]


def test_render_project_fails_loud_without_ffmpeg(client, s3_bucket, monkeypatch):
    # Forced deterministically (not relying on this machine happening to lack ffmpeg —
    # CI runners often ship it preinstalled) so the test is stable everywhere; on this
    # dev machine specifically, ffmpeg is in fact genuinely absent too (see PROGRESS.md).
    monkeypatch.setattr(video_render.shutil, "which", lambda _name: None)

    headers = _auth_headers(client)
    job_id = _successful_job_id(client, headers, s3_bucket)
    project = client.post(
        "/projects",
        json={"title": "Iklan sepatu", "mode": "product_ad", "source_job_id": job_id},
        headers=headers,
    ).json()

    response = client.post(f"/projects/{project['id']}/render", headers=headers)
    assert response.status_code == 202
    body = response.json()
    assert body["render_status"] == "failed"
    assert "ffmpeg" in body["render_error_message"].lower()
