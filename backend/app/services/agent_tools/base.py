"""Shared shape for every AI chat agent tool (Phase 6R). Each concrete tool is a thin
wrapper over an existing service function (`generation_service`, `project_service`,
`publish_service`, ...) — never a reimplementation — so a tool call and the
equivalent HTTP request always run the exact same code path.
"""
from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.user import User
from app.services.llm_providers.base import ToolSpec

# Runs the tool and returns a JSON-serializable result dict, persisted verbatim into
# ChatMessage.tool_result. Raises a domain exception from app.services.errors on
# failure — app.services.chat_agent translates it into a plain-text chat reply.
ToolRunner = Callable[[Session, User, dict], dict]


@dataclass
class AgentTool:
    spec: ToolSpec
    run: ToolRunner
