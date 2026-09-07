"""Fire-and-forget notification to an n8n webhook (Phase 6R-10) — orchestration/
notification only. n8n fans this out to Discord/Slack etc.; it never posts to IG/
TikTok/YouTube directly (developer app approval still pending, see CLAUDE.md). A
notification failure must never break the render/export pipeline it's reporting on,
so every failure mode here is swallowed and logged, never raised.
"""
import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def notify_pipeline_event(event: str, payload: dict) -> None:
    webhook_url = get_settings().n8n_webhook_url
    if not webhook_url:
        return  # disabled — no n8n instance configured yet

    try:
        httpx.post(webhook_url, json={"event": event, **payload}, timeout=5)
    except Exception:
        logger.warning("n8n_notify: gagal mengirim event %r ke webhook", event, exc_info=True)
