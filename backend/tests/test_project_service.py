"""Unit tests for `app.services.project_service` directly (not just through the
`/projects` HTTP layer, which `test_projects.py` already covers) — these are the
functions the AI chat agent's `create_project_tool`/`render_project_tool` (Phase 6R)
will call, so they need exception-level coverage independent of `HTTPException`.
"""
import uuid

import pytest
from moto import mock_aws

import app.models.base as models_base
from app.core.config import get_settings
from app.models.user import User
from app.services.errors import JobNotFoundError, JobNotReadyError, ProjectNotFoundError
from app.services.project_service import create_project_from_job, enqueue_render, get_owned_project
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


def _auth_headers(client, email="proj-service@example.com") -> dict:
    response = client.post(
        "/auth/register", json={"email": email, "password": "hunter22", "name": "Nabil"}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _successful_job(client, s3_bucket, email="proj-service@example.com"):
    headers = _auth_headers(client, email)
    asset = client.post(
        "/media/upload",
        files={"file": ("product.jpg", b"\xff\xd8\xff" + b"fake", "image/jpeg")},
        headers=headers,
    ).json()
    job = client.post(
        "/ai/generate-video", json={"source_asset_id": asset["id"]}, headers=headers
    ).json()
    assert job["status"] == "success"
    return job["id"]


def test_create_project_from_job_success(client, s3_bucket):
    job_id = _successful_job(client, s3_bucket)

    db = models_base.SessionLocal()
    try:
        user = db.query(User).one()
        project = create_project_from_job(db, user, "Iklan sepatu", "product_ad", uuid.UUID(job_id))
        assert project.status == "draft"
        assert project.source_job_id == uuid.UUID(job_id)
    finally:
        db.close()


def test_create_project_from_job_rejects_unknown_job(client, s3_bucket):
    _auth_headers(client)

    db = models_base.SessionLocal()
    try:
        user = db.query(User).one()
        with pytest.raises(JobNotFoundError):
            create_project_from_job(db, user, "X", "product_ad", uuid.uuid4())
    finally:
        db.close()


def test_create_project_from_job_rejects_unfinished_job(client, s3_bucket):
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

    db = models_base.SessionLocal()
    try:
        user = db.query(User).one()
        with pytest.raises(JobNotReadyError):
            create_project_from_job(db, user, "X", "product_ad", uuid.UUID(failed_job["id"]))
    finally:
        db.close()


def test_enqueue_render_rejects_unowned_project(client, s3_bucket):
    _auth_headers(client, email="owner@example.com")
    _auth_headers(client, email="other@example.com")

    db = models_base.SessionLocal()
    try:
        user = db.query(User).filter_by(email="other@example.com").one()
        with pytest.raises(ProjectNotFoundError):
            enqueue_render(db, user, uuid.uuid4())
        with pytest.raises(ProjectNotFoundError):
            get_owned_project(uuid.uuid4(), db, user)
    finally:
        db.close()


def test_enqueue_render_success(client, s3_bucket, monkeypatch):
    import app.workers.tasks as tasks_module

    monkeypatch.setattr(tasks_module, "trim_video", lambda *args, **kwargs: b"fake-mp4-bytes")

    job_id = _successful_job(client, s3_bucket)

    db = models_base.SessionLocal()
    try:
        user = db.query(User).one()
        project = create_project_from_job(db, user, "Iklan sepatu", "product_ad", uuid.UUID(job_id))
        rendered = enqueue_render(db, user, project.id)
        # Celery runs eagerly in tests (see conftest.py) — render already finished.
        assert rendered.render_status == "success"
        assert rendered.final_video_url
    finally:
        db.close()
