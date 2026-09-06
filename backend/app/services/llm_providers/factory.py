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

    if provider_name == "anthropic":
        # Deferred import: keeps the `anthropic` SDK optional at import time — most
        # installs stay on "mock" and never need it constructed.
        from app.services.llm_providers.anthropic_provider import AnthropicLLMProvider

        return AnthropicLLMProvider()

    raise NotImplementedError(
        f"AI_LLM_PROVIDER={provider_name!r} belum diimplementasi. "
        "Provider yang tersedia sekarang: 'mock', 'anthropic'."
    )
