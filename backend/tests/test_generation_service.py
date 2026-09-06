"""Unit tests for `app.services.generation_service` directly (not just through the
`/ai/generate-video` HTTP layer, which `test_ai.py` already covers) — this is the
function the AI chat agent's `generate_video_tool` (Phase 6R) will call, so it needs
its own exception-level coverage independent of `HTTPException`.
"""
import uuid

import pytest
from moto import mock_aws

import app.models.base as models_base
from app.core.config import get_settings
from app.models.media_asset import MediaAsset
from app.models.user import User
from app.services.errors import MediaNotFoundError, QuotaExceededError
from app.services.generation_service import create_generate_video_job
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


def _auth_headers(client, email="gen-service@example.com") -> dict:
    response = client.post(
        "/auth/register", json={"email": email, "password": "hunter22", "name": "Nabil"}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _register_and_upload(client, email="gen-service@example.com"):
    headers = _auth_headers(client, email)
    asset = client.post(
        "/media/upload",
        files={"file": ("product.jpg", b"\xff\xd8\xff" + b"fake", "image/jpeg")},
        headers=headers,
    ).json()
    return headers, asset["id"]


def test_create_generate_video_job_success(client, s3_bucket):
    _register_and_upload(client)

    db = models_base.SessionLocal()
    try:
        user = db.query(User).one()
        asset_id = db.query(MediaAsset).filter_by(user_id=user.id).one().id
        job = create_generate_video_job(db, user, asset_id, "gaya minimalis")
        assert job.status == "success"  # Celery runs eagerly in tests (see conftest.py)
        assert job.result_url
        assert user.ai_generation_used == 1
    finally:
        db.close()


def test_create_generate_video_job_rejects_unknown_asset(client, s3_bucket):
    _register_and_upload(client)

    db = models_base.SessionLocal()
    try:
        user = db.query(User).one()
        with pytest.raises(MediaNotFoundError):
            create_generate_video_job(db, user, uuid.uuid4(), None)
    finally:
        db.close()


def test_create_generate_video_job_enforces_quota(client, s3_bucket):
    _register_and_upload(client)

    db = models_base.SessionLocal()
    try:
        user = db.query(User).one()
        asset_id = db.query(MediaAsset).filter_by(user_id=user.id).one().id

        # Free plan quota is 5 (seeded in conftest.py).
        for _ in range(5):
            create_generate_video_job(db, user, asset_id, None)

        with pytest.raises(QuotaExceededError):
            create_generate_video_job(db, user, asset_id, None)
    finally:
        db.close()
