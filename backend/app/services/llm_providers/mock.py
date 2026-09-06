"""Default LLM provider while no real one is wired in yet (CLAUDE.md: don't hardcode a
provider without confirmation). The user has confirmed Claude (Anthropic API) as the
target real provider (see PROGRESS.md Phase 6R), but this mock stays the *default*
(`AI_LLM_PROVIDER=mock`) so nothing in the app — tests included — ever requires a real
API key to run. Plays the same role `MockVideoProvider` plays for video generation: a
real local implementation that exercises the whole tool-calling pipeline, not a no-op
stub.

Deterministic keyword matching on the latest user message — no network call, no
randomness, fully unit-testable. Never chains tool calls (it has no real reasoning to
decide when a goal is fulfilled) — `app/services/chat_agent.py` calls `complete()`
again after running a tool so a real provider *can* chain, but this mock closes with a
plain reply the moment it sees its own tool result at the end of the history, instead
of matching the same user message and re-running the same tool forever.
"""
from app.services.llm_providers.base import LLMProvider, LLMResponse, ToolCallRequest, ToolSpec

# Order matters: checked top-to-bottom, first match wins — image/audio keywords must
# come before the generic "generate" (video) check so "generate gambar" doesn't get
# routed to generate_video_tool. `arguments` is a function of the raw (non-lowercased)
# message so image/audio tools get *something* usable as prompt/text — a real provider
# would extract this properly; the mock just hands over the whole message.
_KEYWORD_TO_TOOL = (
    (("template",), "apply_template_tool", lambda _text: {}),
    (("gambar", "generate image"), "generate_image_tool", lambda text: {"prompt": text}),
    (
        ("voiceover", "text-to-speech", "suara ai"),
        "generate_voiceover_tool",
        lambda text: {"text": text},
    ),
    (("generate", "buatkan video"), "generate_video_tool", lambda _text: {}),
    (("render",), "render_project_tool", lambda _text: {}),
    (("publish", "siapkan publish", "export"), "prepare_publish_tool", lambda _text: {}),
)


class MockLLMProvider(LLMProvider):
    def complete(self, messages: list[dict], tools: list[ToolSpec]) -> LLMResponse:
        if messages and messages[-1].get("role") == "tool":
            return LLMResponse(message=f"Oke — {messages[-1]['content']}")

        available = {tool.name for tool in tools}
        latest_user_message = next(
            (m["content"] for m in reversed(messages) if m.get("role") == "user"), ""
        )
        text_lower = latest_user_message.lower()

        for keywords, tool_name, build_arguments in _KEYWORD_TO_TOOL:
            if tool_name in available and any(keyword in text_lower for keyword in keywords):
                return LLMResponse(
                    tool_call=ToolCallRequest(
                        name=tool_name, arguments=build_arguments(latest_user_message)
                    )
                )

        return LLMResponse(
            message=(
                "Saya belum bisa memproses permintaan itu secara otomatis (mode mock, "
                "belum ada provider AI asli tersambung). Coba kata kunci seperti "
                "'generate', 'gambar', 'voiceover', 'render', atau 'siapkan publish'."
            )
        )
