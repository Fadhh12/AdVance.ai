"""Picks the configured LLM provider (`AI_LLM_PROVIDER` in .env) — the only place in
the codebase that's allowed to know provider names. Everything else talks to
`LLMProvider`. Mirrors `app/services/ai_providers/factory.py` exactly.
"""
from app.core.config import get_settings
from app.services.llm_providers.base import LLMProvider
from app.services.llm_providers.mock import MockLLMProvider


def get_llm_provider() -> LLMProvider:
    provider_name = get_settings().ai_llm_provider
    if provider_name == "mock":
        return MockLLMProvider()

    if provider_name == "gemini":
        # Deferred import: keeps the `google-genai` SDK optional at import time — most
        # installs stay on "mock" and never need it constructed. This is the
        # recommended real provider for now — free tier, no billing required.
        from app.services.llm_providers.gemini_provider import GeminiLLMProvider

        return GeminiLLMProvider()

    if provider_name == "anthropic":
        # Deferred import, same reasoning. Upgrade path once there's paid traffic to
        # justify it — Claude via Anthropic's API is not free (see PROGRESS.md).
        from app.services.llm_providers.anthropic_provider import AnthropicLLMProvider

        return AnthropicLLMProvider()

    raise NotImplementedError(
        f"AI_LLM_PROVIDER={provider_name!r} belum diimplementasi. "
        "Provider yang tersedia sekarang: 'mock', 'gemini', 'anthropic'."
    )
