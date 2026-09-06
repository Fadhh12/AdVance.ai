"""Orchestrates one turn of the AI chat agent (Phase 6R): persist the user's message,
call the configured `LLMProvider` with the tools available, run at most one tool call
per LLM response, feed the tool's result back in, and repeat (capped) until the
provider returns a plain message instead of another tool call.

Domain exceptions from `app/services/errors.py` (raised by a tool's underlying service
call — e.g. quota exceeded, project not found) are caught here and turned into a
plain tool-result message rather than propagating as a 500 — the chat channel has no
HTTP status codes, so these need to read as normal conversation, not a crash.
"""
import uuid

from sqlalchemy.orm import Session

from app.models.chat import ChatConversation, ChatMessage
from app.models.user import User
from app.services.agent_tools import TOOLS
from app.services.llm_providers.factory import get_llm_provider

MAX_TOOL_CALLS_PER_TURN = 3


def _get_or_create_conversation(
    db: Session,
    current_user: User,
    conversation_id: uuid.UUID | None,
    project_id: uuid.UUID | None,
) -> ChatConversation:
    if conversation_id is not None:
        existing = db.get(ChatConversation, conversation_id)
        if existing is not None and existing.user_id == current_user.id:
            return existing

    conversation = ChatConversation(user_id=current_user.id, project_id=project_id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def _history_as_messages(db: Session, conversation_id: uuid.UUID) -> list[dict]:
    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    return [{"role": row.role, "content": row.content} for row in rows]


def _add_message(
    db: Session,
    conversation_id: uuid.UUID,
    role: str,
    content: str,
    tool_name: str | None = None,
    tool_args: dict | None = None,
    tool_result: dict | None = None,
) -> ChatMessage:
    message = ChatMessage(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_name=tool_name,
        tool_args=tool_args,
        tool_result=tool_result,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def handle_turn(
    db: Session,
    current_user: User,
    content: str,
    conversation_id: uuid.UUID | None,
    project_id: uuid.UUID | None,
    media_asset_id: uuid.UUID | None = None,
) -> tuple[ChatConversation, list[ChatMessage]]:
    conversation = _get_or_create_conversation(db, current_user, conversation_id, project_id)
    produced: list[ChatMessage] = [_add_message(db, conversation.id, "user", content)]

    provider = get_llm_provider()
    tool_specs = [tool.spec for tool in TOOLS.values()]

    for _ in range(MAX_TOOL_CALLS_PER_TURN):
        response = provider.complete(_history_as_messages(db, conversation.id), tool_specs)

        if response.tool_call is None:
            produced.append(_add_message(db, conversation.id, "assistant", response.message or ""))
            return conversation, produced

        tool = TOOLS.get(response.tool_call.name)
        if tool is None:
            unknown_tool_message = f"Tool '{response.tool_call.name}' tidak dikenal."
            produced.append(_add_message(db, conversation.id, "assistant", unknown_tool_message))
            return conversation, produced

        arguments = dict(response.tool_call.arguments)
        # An LLM tool call can't carry the file the user just attached in this turn —
        # thread the id the frontend uploaded moments ago (Phase 6R-6) into any tool
        # that accepts it, without the provider needing to reference it explicitly.
        if (
            media_asset_id is not None
            and "media_asset_id" in tool.spec.parameters.get("properties", {})
            and "media_asset_id" not in arguments
        ):
            arguments["media_asset_id"] = str(media_asset_id)

        try:
            result = tool.run(db, current_user, arguments)
            result_text = f"Tool {tool.spec.name} berhasil: {result}"
        except Exception as exc:  # noqa: BLE001 — domain errors from services/*_service.py
            result = {"error": str(exc)}
            result_text = str(exc)

        produced.append(
            _add_message(
                db,
                conversation.id,
                "tool",
                result_text,
                tool_name=tool.spec.name,
                tool_args=arguments,
                tool_result=result,
            )
        )

    # Hit the tool-call cap — close the turn instead of looping forever on a runaway
    # provider response.
    produced.append(
        _add_message(
            db,
            conversation.id,
            "assistant",
            "Sudah mencoba beberapa langkah tapi belum selesai — coba lebih spesifik?",
        )
    )
    return conversation, produced
