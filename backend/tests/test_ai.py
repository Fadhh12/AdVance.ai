import pytest
from moto import mock_aws

from app.core.config import get_settings
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


def _auth_headers(client, email="ai@example.com") -> dict:
    response = client.post(
        "/auth/register", json={"email": email, "password": "hunter22", "name": "Nabil"}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _upload_photo(client, headers) -> str:
    response = client.post(
        "/media/upload",
        files={"file": ("product.jpg", b"\xff\xd8\xff" + b"fake", "image/jpeg")},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_generate_video_success_runs_synchronously_in_tests(client, s3_bucket):
    headers = _auth_headers(client)
    asset_id = _upload_photo(client, headers)

    response = client.post(
        "/ai/generate-video", json={"source_asset_id": asset_id}, headers=headers
    )
    assert response.status_code == 202
    job = response.json()
    # Celery runs eagerly in tests (see conftest.py) — by the time the request
    # returns, the job has already gone through queued -> processing -> success.
    assert job["status"] == "success"
    assert job["result_url"]

    job_response = client.get(f"/ai/jobs/{job['id']}", headers=headers)
    assert job_response.status_code == 200
    assert job_response.json()["status"] == "success"


def test_generate_video_provider_failure_marks_job_failed(client, s3_bucket):
    headers = _auth_headers(client)
    asset_id = _upload_photo(client, headers)

    response = client.post(
        "/ai/generate-video",
        json={"source_asset_id": asset_id, "prompt": "please trigger-failure now"},
        headers=headers,
    )
    assert response.status_code == 202
    job = response.json()
    assert job["status"] == "failed"
    assert job["error_message"]


def test_generate_video_rejects_unknown_source_asset(client, s3_bucket):
    headers = _auth_headers(client)
    response = client.post(
        "/ai/generate-video",
        json={"source_asset_id": "00000000-0000-0000-0000-000000000099"},
        headers=headers,
    )
    assert response.status_code == 404


def test_generate_video_enforces_quota_before_running_job(client, s3_bucket):
    headers = _auth_headers(client)
    asset_id = _upload_photo(client, headers)

    # Free plan quota is 5 (seeded in conftest.py) — the 6th request must be rejected.
    for _ in range(5):
        response = client.post(
            "/ai/generate-video", json={"source_asset_id": asset_id}, headers=headers
        )
        assert response.status_code == 202

    over_quota_response = client.post(
        "/ai/generate-video", json={"source_asset_id": asset_id}, headers=headers
    )
    assert over_quota_response.status_code == 402


def test_get_job_requires_ownership(client, s3_bucket):
    headers_a = _auth_headers(client, email="owner@example.com")
    headers_b = _auth_headers(client, email="other@example.com")
    asset_id = _upload_photo(client, headers_a)

    job = client.post(
        "/ai/generate-video", json={"source_asset_id": asset_id}, headers=headers_a
    ).json()

    forbidden = client.get(f"/ai/jobs/{job['id']}", headers=headers_b)
    assert forbidden.status_code == 404
