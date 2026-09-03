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


def _auth_headers(client, email="publish@example.com") -> dict:
    response = client.post(
        "/auth/register", json={"email": email, "password": "hunter22", "name": "Nabil"}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _rendered_project(client, headers, monkeypatch) -> dict:
    """Registers, uploads, generates, creates a project, and renders it (trim_video
    mocked) — the full pipeline a project needs to go through before Publish Manual
    Assist becomes available.
    """
    monkeypatch.setattr(tasks_module, "trim_video", lambda *a, **kw: b"fake-mp4-bytes")

    asset = client.post(
        "/media/upload",
        files={"file": ("product.jpg", b"\xff\xd8\xff" + b"fake", "image/jpeg")},
        headers=headers,
    ).json()
    job = client.post(
        "/ai/generate-video", json={"source_asset_id": asset["id"]}, headers=headers
    ).json()
    project = client.post(
        "/projects",
        json={"title": "Sepatu lari", "mode": "product_ad", "source_job_id": job["id"]},
        headers=headers,
    ).json()
    client.patch(
        f"/projects/{project['id']}", json={"caption": "x" * 2300}, headers=headers
    )
    rendered = client.post(f"/projects/{project['id']}/render", headers=headers).json()
    assert rendered["render_status"] == "success"
    return rendered


def test_create_posts_requires_successful_render(client, s3_bucket, monkeypatch):
    headers = _auth_headers(client)
    asset = client.post(
        "/media/upload",
        files={"file": ("product.jpg", b"\xff\xd8\xff" + b"fake", "image/jpeg")},
        headers=headers,
    ).json()
    job = client.post(
        "/ai/generate-video", json={"source_asset_id": asset["id"]}, headers=headers
    ).json()
    project = client.post(
        "/projects",
        json={"title": "Sepatu lari", "mode": "product_ad", "source_job_id": job["id"]},
        headers=headers,
    ).json()

    response = client.post(f"/projects/{project['id']}/posts", headers=headers)
    assert response.status_code == 409


def test_create_posts_exports_one_per_platform(client, s3_bucket, monkeypatch):
    headers = _auth_headers(client)
    project = _rendered_project(client, headers, monkeypatch)

    monkeypatch.setattr(
        tasks_module, "export_for_platform", lambda *a, **kw: b"fake-export-bytes"
    )

    response = client.post(f"/projects/{project['id']}/posts", headers=headers)
    assert response.status_code == 202
    posts = response.json()
    assert {p["platform"] for p in posts} == {"instagram", "tiktok", "youtube"}
    for post in posts:
        assert post["export_status"] == "success"
        assert post["status"] == "manual_ready"
        assert post["video_url"]
        # caption was auto-truncated to the platform limit (SRS §2.2)
        assert len(post["caption"]) <= 2200 if post["platform"] != "youtube" else 5000

    youtube_post = next(p for p in posts if p["platform"] == "youtube")
    assert youtube_post["youtube_title"] == "Sepatu lari"


def test_create_posts_export_fails_loud_without_ffmpeg(client, s3_bucket, monkeypatch):
    monkeypatch.setattr(video_render.shutil, "which", lambda _name: None)

    headers = _auth_headers(client)
    project = _rendered_project(client, headers, monkeypatch)

    response = client.post(f"/projects/{project['id']}/posts", headers=headers)
    posts = response.json()
    assert all(p["export_status"] == "failed" for p in posts)
    assert all("ffmpeg" in p["export_error_message"].lower() for p in posts)


def test_mark_uploaded_requires_export_success(client, s3_bucket, monkeypatch):
    headers = _auth_headers(client)
    project = _rendered_project(client, headers, monkeypatch)
    monkeypatch.setattr(
        tasks_module, "export_for_platform", lambda *a, **kw: b"fake-export-bytes"
    )
    posts = client.post(f"/projects/{project['id']}/posts", headers=headers).json()
    post_id = posts[0]["id"]

    response = client.post(f"/posts/{post_id}/mark-uploaded", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "manual_uploaded"

    # Already-uploaded posts can't be re-marked from a non-ready state.
    second_attempt = client.post(f"/posts/{post_id}/mark-uploaded", headers=headers)
    assert second_attempt.status_code == 409


def test_share_qr_returns_png(client, s3_bucket, monkeypatch):
    headers = _auth_headers(client)
    project = _rendered_project(client, headers, monkeypatch)
    monkeypatch.setattr(
        tasks_module, "export_for_platform", lambda *a, **kw: b"fake-export-bytes"
    )
    posts = client.post(f"/projects/{project['id']}/posts", headers=headers).json()
    post_id = posts[0]["id"]

    response = client.get(f"/posts/{post_id}/qr", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_list_all_posts_backs_content_calendar(client, s3_bucket, monkeypatch):
    headers_a = _auth_headers(client, email="calendar-a@example.com")
    headers_b = _auth_headers(client, email="calendar-b@example.com")
    project = _rendered_project(client, headers_a, monkeypatch)
    monkeypatch.setattr(
        tasks_module, "export_for_platform", lambda *a, **kw: b"fake-export-bytes"
    )
    client.post(f"/projects/{project['id']}/posts", headers=headers_a)

    own_posts = client.get("/posts", headers=headers_a).json()
    assert len(own_posts) == 3
    assert all(p["project_title"] == "Sepatu lari" for p in own_posts)

    other_posts = client.get("/posts", headers=headers_b).json()
    assert other_posts == []


def test_posts_require_ownership(client, s3_bucket, monkeypatch):
    headers_a = _auth_headers(client, email="owner2@example.com")
    headers_b = _auth_headers(client, email="other2@example.com")
    project = _rendered_project(client, headers_a, monkeypatch)
    monkeypatch.setattr(
        tasks_module, "export_for_platform", lambda *a, **kw: b"fake-export-bytes"
    )
    posts = client.post(f"/projects/{project['id']}/posts", headers=headers_a).json()

    forbidden = client.get(f"/projects/{project['id']}/posts", headers=headers_b)
    assert forbidden.status_code == 404

    forbidden_mark = client.post(
        f"/posts/{posts[0]['id']}/mark-uploaded", headers=headers_b
    )
    assert forbidden_mark.status_code == 404
