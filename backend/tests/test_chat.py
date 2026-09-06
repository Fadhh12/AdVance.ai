"""AI chat agent (Phase 6R-3). Uses the default `AI_LLM_PROVIDER=mock` (see
app/services/llm_providers/mock.py) — no real Anthropic call happens in this suite,
ever; that's the whole point of the mock staying the default until a real key is set.
"""
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


def _auth_headers(client, email="chat@example.com") -> dict:
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
    return response.json()["id"]


def test_generate_video_via_chat_creates_real_job(client, s3_bucket):
    headers = _auth_headers(client)
    _upload_photo(client, headers)

    response = client.post(
        "/chat/messages",
        json={"content": "tolong generate video dari foto ini dong"},
        headers=headers,
    )
    assert response.status_code == 201
    body = response.json()
    roles = [m["role"] for m in body["messages"]]
    assert roles == ["user", "tool", "assistant"]

    tool_message = body["messages"][1]
    assert tool_message["tool_name"] == "generate_video_tool"
    assert tool_message["tool_result"]["status"] == "success"
    assert tool_message["tool_result"]["job_id"]


def test_quota_exceeded_surfaces_as_chat_reply_not_500(client, s3_bucket):
    headers = _auth_headers(client)
    _upload_photo(client, headers)

    # Free plan quota is 5 (seeded in conftest.py) — burn it via chat, one job per turn
    # (a fresh conversation each time so the mock always sees an unmatched-tool-result
    # last message and doesn't short-circuit).
    for _ in range(5):
        response = client.post(
            "/chat/messages", json={"content": "generate video"}, headers=headers
        )
        assert response.status_code == 201

    over_quota = client.post(
        "/chat/messages", json={"content": "generate video lagi"}, headers=headers
    )
    assert over_quota.status_code == 201  # never a raw 500
    tool_message = over_quota.json()["messages"][1]
    assert tool_message["role"] == "tool"
    assert "kuota" in tool_message["content"].lower()


def test_prepare_publish_tool_never_touches_real_social_apis(client, s3_bucket, monkeypatch):
    import app.workers.tasks as tasks_module

    monkeypatch.setattr(tasks_module, "trim_video", lambda *args, **kwargs: b"fake-mp4-bytes")
    monkeypatch.setattr(
        tasks_module, "export_for_platform", lambda *args, **kwargs: b"fake-export-bytes"
    )

    headers = _auth_headers(client)
    _upload_photo(client, headers)

    gen = client.post(
        "/chat/messages", json={"content": "generate video"}, headers=headers
    ).json()
    job_id = gen["messages"][1]["tool_result"]["job_id"]

    project = client.post(
        "/projects",
        json={"title": "Iklan sepatu", "mode": "product_ad", "source_job_id": job_id},
        headers=headers,
    ).json()
    client.post(f"/projects/{project['id']}/render", headers=headers)

    publish = client.post(
        "/chat/messages", json={"content": "siapkan publish dong"}, headers=headers
    )
    assert publish.status_code == 201
    tool_message = publish.json()["messages"][1]
    assert tool_message["tool_name"] == "prepare_publish_tool"
    posts = tool_message["tool_result"]["posts"]
    assert {p["platform"] for p in posts} == {"instagram", "tiktok", "youtube"}


def test_conversation_history_round_trip(client, s3_bucket):
    headers = _auth_headers(client)

    first = client.post(
        "/chat/messages", json={"content": "halo, apa kabar?"}, headers=headers
    ).json()
    conversation_id = first["conversation_id"]

    second = client.post(
        "/chat/messages",
        json={"content": "masih ada?", "conversation_id": conversation_id},
        headers=headers,
    )
    assert second.status_code == 201
    assert second.json()["conversation_id"] == conversation_id

    history = client.get(f"/chat/conversations/{conversation_id}/messages", headers=headers)
    assert history.status_code == 200
    assert len(history.json()) == 4  # 2 user + 2 assistant (no tool call — small talk)


def test_conversation_history_requires_ownership(client, s3_bucket):
    headers_a = _auth_headers(client, email="owner@example.com")
    headers_b = _auth_headers(client, email="other@example.com")

    conversation_id = client.post(
        "/chat/messages", json={"content": "halo"}, headers=headers_a
    ).json()["conversation_id"]

    forbidden = client.get(
        f"/chat/conversations/{conversation_id}/messages", headers=headers_b
    )
    assert forbidden.status_code == 404
