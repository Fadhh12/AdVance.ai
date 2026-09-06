"""Unit tests for the LLM provider abstraction (Phase 6R). Mirrors the style of
`test_ai.py`'s coverage of `MockVideoProvider`: no network, no real provider needed —
`AI_LLM_PROVIDER` defaults to "mock", and the factory fails loud on anything else that
isn't implemented yet.
"""
import pytest

from app.core.config import get_settings
from app.services.llm_providers.base import ToolSpec
from app.services.llm_providers.factory import get_llm_provider
from app.services.llm_providers.mock import MockLLMProvider

_TOOLS = [
    ToolSpec(name="generate_video_tool", description="", parameters={}),
    ToolSpec(name="render_project_tool", description="", parameters={}),
    ToolSpec(name="prepare_publish_tool", description="", parameters={}),
    ToolSpec(name="apply_template_tool", description="", parameters={}),
]


def test_factory_returns_mock_by_default():
    assert get_settings().ai_llm_provider == "mock"
    assert isinstance(get_llm_provider(), MockLLMProvider)


def test_factory_fails_loud_on_unimplemented_provider(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "ai_llm_provider", "openai")
    with pytest.raises(NotImplementedError):
        get_llm_provider()


@pytest.mark.parametrize(
    ("message", "expected_tool"),
    [
        ("Tolong generate video dari foto ini", "generate_video_tool"),
        ("buatkan video gaya affiliate", "generate_video_tool"),
        ("render videonya dong", "render_project_tool"),
        ("siapkan publish ke instagram", "prepare_publish_tool"),
        ("pakai template unboxing", "apply_template_tool"),
    ],
)
def test_mock_llm_provider_maps_keywords_to_tools(message, expected_tool):
    response = MockLLMProvider().complete(
        messages=[{"role": "user", "content": message}], tools=_TOOLS
    )
    assert response.tool_call is not None
    assert response.tool_call.name == expected_tool


def test_mock_llm_provider_falls_back_to_plain_message_when_unmatched():
    response = MockLLMProvider().complete(
        messages=[{"role": "user", "content": "halo, apa kabar?"}], tools=_TOOLS
    )
    assert response.tool_call is None
    assert response.message


def test_mock_llm_provider_never_calls_a_tool_not_offered():
    response = MockLLMProvider().complete(
        messages=[{"role": "user", "content": "tolong generate video"}], tools=[]
    )
    assert response.tool_call is None


def test_mock_llm_provider_stops_after_one_tool_call_per_turn():
    # If the orchestrator loops `complete()` again after running a tool, the mock must
    # not re-match the same (unchanged) user message and call the same tool again —
    # that would silently repeat side effects (e.g. burning quota) on every iteration.
    messages = [
        {"role": "user", "content": "generate video dari foto ini"},
        {"role": "tool", "content": "Tool generate_video_tool berhasil: {...}"},
    ]
    response = MockLLMProvider().complete(messages=messages, tools=_TOOLS)
    assert response.tool_call is None
    assert response.message
