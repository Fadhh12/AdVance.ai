"""AI chat agent conversation/message persistence (Phase 6R). A conversation is
scoped to one user (and optionally one in-progress project); each message is either
what the user typed, what the assistant replied, or the JSON result of a tool call the
agent made in between — see `app/services/chat_agent.py` for the orchestration loop
and `app/services/agent_tools/` for the tools themselves.
"""
import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ChatConversation(Base):
    __tablename__ = "chat_conversations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("content_projects.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chat_conversations.id"), index=True
    )
    role: Mapped[str] = mapped_column(String(20))  # user | assistant | tool
    content: Mapped[str] = mapped_column(Text)

    # Populated only on tool-call/tool-result messages (role == "tool").
    tool_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tool_args: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    tool_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
