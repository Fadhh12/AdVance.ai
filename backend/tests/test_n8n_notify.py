"""Phase 6R-10 — n8n_notify must never raise regardless of webhook state, and must be a
true no-op when N8N_WEBHOOK_URL is empty (the default — no n8n instance configured).
"""
from app.core.config import get_settings
from app.services import n8n_notify


def test_noop_when_webhook_url_empty(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "n8n_webhook_url", "")

    def _fail_if_called(*args, **kwargs):
        raise AssertionError("httpx.post should not be called when webhook_url is empty")

    monkeypatch.setattr(n8n_notify.httpx, "post", _fail_if_called)

    n8n_notify.notify_pipeline_event("render.success", {"project_id": "abc"})


def test_posts_event_payload_when_configured(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "n8n_webhook_url", "http://localhost:5678/webhook/test")

    calls = []
    monkeypatch.setattr(
        n8n_notify.httpx, "post", lambda url, json, timeout: calls.append((url, json))
    )

    n8n_notify.notify_pipeline_event("render.success", {"project_id": "abc"})

    assert len(calls) == 1
    url, payload = calls[0]
    assert url == "http://localhost:5678/webhook/test"
    assert payload == {"event": "render.success", "project_id": "abc"}


def test_swallows_network_failure(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "n8n_webhook_url", "http://localhost:5678/webhook/test")

    def _boom(*args, **kwargs):
        raise ConnectionError("n8n not running")

    monkeypatch.setattr(n8n_notify.httpx, "post", _boom)

    # Must not raise.
    n8n_notify.notify_pipeline_event("render.failed", {"project_id": "abc"})
