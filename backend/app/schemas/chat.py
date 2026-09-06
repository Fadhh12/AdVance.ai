import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatMessageIn(BaseModel):
    content: str
    conversation_id: uuid.UUID | None = None
    project_id: uuid.UUID | None = None
    # Set by the frontend right after a real POST /media/upload call (Phase 6R-6) so
    # select_media_tool/generate_video_tool can resolve "foto ini" without the LLM
    # needing to carry a file — chat can't transmit bytes.
    media_asset_id: uuid.UUID | None = None


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: str
    content: str
    tool_name: str | None
    tool_result: dict | None
    created_at: datetime


class ChatTurnOut(BaseModel):
    conversation_id: uuid.UUID
    messages: list[ChatMessageOut]
