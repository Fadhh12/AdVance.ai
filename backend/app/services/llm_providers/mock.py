"""Default LLM provider while no real one is wired in yet (CLAUDE.md: don't hardcode a
provider without confirmation). The user has confirmed Claude (Anthropic API) as the
target real provider (see PROGRESS.md Phase 6R), but this mock stays the *default*
(`AI_LLM_PROVIDER=mock`) so nothing in the app — tests included — ever requires a real
API key to run. Plays the same role `MockVideoProvider` plays for video generation: a
real local implementation that exercises the whole tool-calling pipeline, not a no-op
stub.

Deterministic keyword matching on the latest user message — no network call, no
randomness, fully unit-testable.
"""
from app.services.llm_providers.base import LLMProvider, LLMResponse, ToolCallRequest, ToolSpec

_KEYWORD_TO_TOOL = (
    (("template",), "apply_template_tool"),
    (("generate", "buatkan video"), "generate_video_tool"),
    (("render",), "render_project_tool"),
    (("publish", "siapkan publish", "export"), "prepare_publish_tool"),
)


class MockLLMProvider(LLMProvider):
    def complete(self, messages: list[dict], tools: list[ToolSpec]) -> LLMResponse:
        available = {tool.name for tool in tools}
        latest_user_message = next(
            (m["content"] for m in reversed(messages) if m.get("role") == "user"), ""
        )
        text = latest_user_message.lower()

        for keywords, tool_name in _KEYWORD_TO_TOOL:
            if tool_name in available and any(keyword in text for keyword in keywords):
                return LLMResponse(tool_call=ToolCallRequest(name=tool_name, arguments={}))

        return LLMResponse(
            message=(
                "Saya belum bisa memproses permintaan itu secara otomatis (mode mock, "
                "belum ada provider AI asli tersambung). Coba kata kunci seperti "
                "'generate', 'render', atau 'siapkan publish'."
            )
        )
