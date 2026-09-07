"""Phase 6R-9 — real TTS provider. `_synthesize_bytes` (the only network-touching
function) is monkeypatched so this suite never makes a real call out to Microsoft's
edge-tts service.
"""
from moto import mock_aws

from app.core.config import get_settings
from app.services.ai_providers import edge_tts_voiceover
from app.services.ai_providers.edge_tts_voiceover import EdgeTTSVoiceoverProvider
from app.services.ai_providers.factory import get_voiceover_provider
from app.services.storage import get_s3_client


def test_synthesize_success_uploads_and_returns_key(monkeypatch):
    monkeypatch.setattr(edge_tts_voiceover, "_synthesize_bytes", lambda text, voice: b"fake-mp3")

    settings = get_settings()
    original_endpoint = settings.s3_endpoint_url
    settings.s3_endpoint_url = None
    try:
        with mock_aws():
            get_s3_client().create_bucket(Bucket=settings.s3_bucket_name)
            result = EdgeTTSVoiceoverProvider().synthesize("Halo, ini teks contoh.")
    finally:
        settings.s3_endpoint_url = original_endpoint

    assert result.success is True
    assert result.audio_key.startswith("voiceover/")
    assert result.audio_key.endswith(".mp3")


def test_synthesize_failure_returns_error_not_raise(monkeypatch):
    def _boom(text, voice):
        raise RuntimeError("network blip")

    monkeypatch.setattr(edge_tts_voiceover, "_synthesize_bytes", _boom)

    result = EdgeTTSVoiceoverProvider().synthesize("Halo")
    assert result.success is False
    assert "TTS gagal" in result.error_message


def test_factory_returns_edge_tts_provider_when_configured(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "ai_voiceover_provider", "edge_tts")

    provider = get_voiceover_provider()
    assert isinstance(provider, EdgeTTSVoiceoverProvider)


def test_factory_fails_loud_for_unknown_provider(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "ai_voiceover_provider", "elevenlabs")

    try:
        get_voiceover_provider()
        raise AssertionError("expected NotImplementedError")
    except NotImplementedError as exc:
        assert "elevenlabs" in str(exc)
