"""AI Image / AI Audio skills (Phase 6R) — new provider interfaces + agent tools.
Mirrors test_ai.py's style for MockVideoProvider: exercise the real mock
implementation (real Pillow/ffmpeg output), not a stubbed-out fake.
"""
import pytest
from moto import mock_aws

from app.core.config import get_settings
from app.services import video_render
from app.services.ai_providers.factory import get_image_provider, get_voiceover_provider
from app.services.ai_providers.mock_image import MockImageProvider
from app.services.ai_providers.mock_voiceover import MockVoiceoverProvider
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


def _auth_headers(client, email="skills@example.com") -> dict:
    response = client.post(
        "/auth/register", json={"email": email, "password": "hunter22", "name": "Nabil"}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_image_factory_returns_mock_by_default():
    assert get_settings().ai_image_provider == "mock"
    assert isinstance(get_image_provider(), MockImageProvider)


def test_image_factory_fails_loud_on_unimplemented_provider(monkeypatch):
    monkeypatch.setattr(get_settings(), "ai_image_provider", "dalle")
    with pytest.raises(NotImplementedError):
        get_image_provider()


def test_voiceover_factory_returns_mock_by_default():
    assert get_settings().ai_voiceover_provider == "mock"
    assert isinstance(get_voiceover_provider(), MockVoiceoverProvider)


def test_voiceover_factory_fails_loud_on_unimplemented_provider(monkeypatch):
    monkeypatch.setattr(get_settings(), "ai_voiceover_provider", "elevenlabs")
    with pytest.raises(NotImplementedError):
        get_voiceover_provider()


def test_mock_image_provider_produces_real_png(s3_bucket):
    result = MockImageProvider().generate_image("sepatu lari warna biru")
    assert result.success
    assert result.result_key
    assert result.result_key.endswith(".png")


def test_mock_voiceover_provider_produces_real_audio(s3_bucket):
    result = MockVoiceoverProvider().synthesize("Halo, ini contoh voiceover.")
    assert result.success
    assert result.audio_key
    assert result.audio_key.endswith(".mp3")


def test_mock_voiceover_provider_fails_loud_without_ffmpeg(s3_bucket, monkeypatch):
    monkeypatch.setattr(video_render.shutil, "which", lambda _name: None)
    result = MockVoiceoverProvider().synthesize("Teks apapun.")
    assert not result.success
    assert "ffmpeg" in result.error_message.lower()


def test_generate_image_via_chat_creates_photo_asset(client, s3_bucket):
    headers = _auth_headers(client)
    response = client.post(
        "/chat/messages",
        json={"content": "tolong bikin gambar produk sepatu warna merah"},
        headers=headers,
    )
    assert response.status_code == 201
    tool_message = response.json()["messages"][1]
    assert tool_message["tool_name"] == "generate_image_tool"
    asset_id = tool_message["tool_result"]["media_asset_id"]

    media = client.get("/media", headers=headers).json()
    created = next(a for a in media if a["id"] == asset_id)
    assert created["type"] == "photo"


def test_generate_voiceover_via_chat_creates_audio_asset(client, s3_bucket):
    headers = _auth_headers(client)
    response = client.post(
        "/chat/messages",
        json={"content": "buatkan voiceover: selamat datang di toko kami"},
        headers=headers,
    )
    assert response.status_code == 201
    tool_message = response.json()["messages"][1]
    assert tool_message["tool_name"] == "generate_voiceover_tool"
    asset_id = tool_message["tool_result"]["media_asset_id"]

    media = client.get("/media", headers=headers).json()
    created = next(a for a in media if a["id"] == asset_id)
    assert created["type"] == "audio"
