"""Abstract interface every LLM/chat-agent provider wrapper must implement.

CLAUDE.md's provider-abstraction rule (originally written for AI video/TTS providers,
see `app/services/ai_providers/base.py`) applies here too: no LLM provider gets
hardcoded without user confirmation. Everything outside `services/llm_providers/`
talks to a provider through this interface only, so swapping providers means adding
one file here, not touching `app/services/chat_agent.py` or any router.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ToolSpec:
    """One tool the LLM is allowed to call, in the shape its tool-calling API expects."""

    name: str
    description: str
    parameters: dict  # JSON Schema for the tool's arguments


@dataclass
class ToolCallRequest:
    name: str
    arguments: dict


@dataclass
class LLMResponse:
    message: str | None = None
    tool_call: ToolCallRequest | None = None


class LLMProvider(ABC):
    """One implementation per provider (e.g. `anthropic_provider.py`). Never call a
    provider's SDK/HTTP API directly from routers, services, or Celery tasks — always
    go through this interface.
    """

    @abstractmethod
    def complete(self, messages: list[dict], tools: list[ToolSpec]) -> LLMResponse:
        """Given the conversation so far (`messages`, each `{"role": ..., "content":
        ...}`) and the tools currently available, return either a plain assistant
        message or a request to call exactly one tool.
        `app/services/chat_agent.py` (Phase 6R) loops this call, feeding each tool's
        result back in as a new message, until the provider returns a plain message
        instead of another tool call.
        """
        raise NotImplementedError
