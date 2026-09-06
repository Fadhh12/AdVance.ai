"""Real LLM provider: Claude via the Anthropic Messages API (Phase 6R-3). Only
constructed when `AI_LLM_PROVIDER=anthropic` — the factory
(`app/services/llm_providers/factory.py`) still defaults to `MockLLMProvider`, so this
is never on the hot path until the user opts in by setting `ANTHROPIC_API_KEY` in
`.env` (see PROGRESS.md Phase 6R-3 for the manual follow-up).

Known simplification: the shared `LLMProvider.complete()` contract passes history as
plain `{"role", "content"}` dicts (role one of user/assistant/tool — see
`app/services/chat_agent.py`), not Anthropic's own richer `tool_use`/`tool_result`
content-block structure. This provider maps a `"tool"` message to an Anthropic
`"user"` message whose content is a plain-text description of the tool result, rather
than a native `tool_result` block tied to a `tool_use_id`. That keeps the shared
interface provider-agnostic (a future non-Anthropic provider doesn't need Anthropic's
block shape either) at the cost of Claude seeing tool outcomes as prose instead of a
structured tool result — acceptable for now; revisit if response quality in practice
calls for it.
"""
from anthropic import Anthropic

from app.core.config import get_settings
from app.services.llm_providers.base import LLMProvider, LLMResponse, ToolCallRequest, ToolSpec


class AnthropicLLMProvider(LLMProvider):
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.anthropic_api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY belum diisi di .env — tidak bisa memakai "
                "AI_LLM_PROVIDER=anthropic tanpa itu."
            )
        self._client = Anthropic(api_key=settings.anthropic_api_key)
        self._model = settings.anthropic_model

    def complete(self, messages: list[dict], tools: list[ToolSpec]) -> LLMResponse:
        anthropic_messages = [
            {
                "role": "assistant" if message["role"] == "assistant" else "user",
                "content": message["content"],
            }
            for message in messages
        ]
        anthropic_tools = [
            {"name": tool.name, "description": tool.description, "input_schema": tool.parameters}
            for tool in tools
        ]

        response = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            messages=anthropic_messages,
            tools=anthropic_tools or None,
        )

        for block in response.content:
            if block.type == "tool_use":
                return LLMResponse(
                    tool_call=ToolCallRequest(name=block.name, arguments=block.input)
                )

        text = "".join(block.text for block in response.content if block.type == "text")
        return LLMResponse(message=text or None)
