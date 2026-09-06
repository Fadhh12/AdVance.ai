"""Real LLM provider: Google Gemini via the `google-genai` SDK (Phase 6R). Chosen as
the **default real provider** because it has a genuinely free tier (Google AI Studio —
no billing required, unlike Anthropic's API) with solid function-calling support —
appropriate while adVance.AI has no revenue yet. `AnthropicLLMProvider` stays in the
codebase behind the same interface as the upgrade path once there's paid traffic to
justify it (swap `AI_LLM_PROVIDER`, nothing else changes).

Only constructed when `AI_LLM_PROVIDER=gemini` — the factory still defaults to
`MockLLMProvider`, so this needs `GEMINI_API_KEY` (free, from
https://aistudio.google.com/apikey) set before it's ever used.

Same known simplification as `anthropic_provider.py`: the shared `LLMProvider.complete()`
contract passes history as plain `{"role", "content"}` dicts, not Gemini's native
`functionCall`/`functionResponse` parts tied to a call id. A `"tool"` message is mapped
to a `"user"` turn with the result as plain text instead of a structured function
response — keeps the interface provider-agnostic at the cost of Gemini seeing tool
outcomes as prose.
"""
from google import genai
from google.genai import types

from app.core.config import get_settings
from app.services.llm_providers.base import LLMProvider, LLMResponse, ToolCallRequest, ToolSpec


class GeminiLLMProvider(LLMProvider):
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY belum diisi di .env — daftar gratis dulu di "
                "https://aistudio.google.com/apikey sebelum memakai AI_LLM_PROVIDER=gemini."
            )
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model = settings.gemini_model

    def complete(self, messages: list[dict], tools: list[ToolSpec]) -> LLMResponse:
        contents = [
            types.Content(
                role="model" if message["role"] == "assistant" else "user",
                parts=[types.Part(text=message["content"])],
            )
            for message in messages
        ]

        config = None
        if tools:
            function_declarations = [
                types.FunctionDeclaration(
                    name=tool.name, description=tool.description, parameters=tool.parameters
                )
                for tool in tools
            ]
            config = types.GenerateContentConfig(
                tools=[types.Tool(function_declarations=function_declarations)]
            )

        response = self._client.models.generate_content(
            model=self._model, contents=contents, config=config
        )

        parts = response.candidates[0].content.parts if response.candidates else []
        for part in parts:
            if part.function_call:
                return LLMResponse(
                    tool_call=ToolCallRequest(
                        name=part.function_call.name, arguments=dict(part.function_call.args or {})
                    )
                )

        text = "".join(part.text for part in parts if part.text)
        return LLMResponse(message=text or None)
