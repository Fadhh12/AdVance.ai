import io

import pytest
from fastapi import HTTPException
from moto import mock_aws

from app.api.media import PHOTO_MAX_BYTES, VIDEO_MAX_BYTES, _read_with_limit
from app.core.config import get_settings
from app.services.storage import get_s3_client


def test_read_with_limit_rejects_oversized_stream():
    stream = io.BytesIO(b"x" * 100)
    with pytest.raises(HTTPException) as exc_info:
        _read_with_limit(stream, max_bytes=50)
    assert exc_info.value.status_code == 413


def test_read_with_limit_accepts_stream_within_bounds():
    stream = io.BytesIO(b"x" * 40)
    spooled, size = _read_with_limit(stream, max_bytes=50)
    assert size == 40
    assert spooled.read() == b"x" * 40


def _auth_headers(client) -> dict:
    response = client.post(
        "/auth/register",
        json={"email": "media@example.com", "password": "hunter22", "name": "Nabil"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def s3_bucket():
    # moto only intercepts calls to real AWS endpoints — drop our MinIO endpoint_url
    # override for the duration of the test so boto3 hits (mocked) AWS S3 instead.
    settings = get_settings()
    original_endpoint = settings.s3_endpoint_url
    settings.s3_endpoint_url = None
    try:
        with mock_aws():
            get_s3_client().create_bucket(Bucket=settings.s3_bucket_name)
            yield
    finally:
        settings.s3_endpoint_url = original_endpoint


def test_upload_rejects_unsupported_content_type(client, s3_bucket):
    headers = _auth_headers(client)
    response = client.post(
        "/media/upload",
        files={"file": ("notes.txt", b"hello", "text/plain")},
        headers=headers,
    )
    assert response.status_code == 415


def test_upload_list_and_delete_photo(client, s3_bucket):
    headers = _auth_headers(client)

    upload_response = client.post(
        "/media/upload",
        files={"file": ("product.jpg", b"\xff\xd8\xff" + b"fake-jpeg-bytes", "image/jpeg")},
        headers=headers,
    )
    assert upload_response.status_code == 201
    body = upload_response.json()
    assert body["type"] == "photo"
    assert body["url"]  # signed URL generated, not a raw stored one

    list_response = client.get("/media", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    delete_response = client.delete(f"/media/{body['id']}", headers=headers)
    assert delete_response.status_code == 204

    empty_list_response = client.get("/media", headers=headers)
    assert empty_list_response.json() == []


def test_upload_requires_auth(client, s3_bucket):
    response = client.post(
        "/media/upload",
        files={"file": ("product.jpg", b"\xff\xd8\xff", "image/jpeg")},
    )
    assert response.status_code == 401


def test_media_max_size_constants_match_srs():
    # SRS §2.2: foto <=20MB, video mentah <=500MB
    assert PHOTO_MAX_BYTES == 20 * 1024 * 1024
    assert VIDEO_MAX_BYTES == 500 * 1024 * 1024
