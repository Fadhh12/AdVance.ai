"""AI chat agent endpoints (Phase 6R). `POST /chat/messages` runs one turn (see
`app/services/chat_agent.py`); `GET /chat/conversations/{id}/messages` reloads history
for a conversation the current user owns.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.models.base import get_db
from app.models.chat import ChatConversation, ChatMessage
from app.models.user import User
from app.schemas.chat import ChatMessageIn, ChatMessageOut, ChatTurnOut
from app.services.chat_agent import handle_turn

router = APIRouter()


@router.post("/messages", response_model=ChatTurnOut, status_code=status.HTTP_201_CREATED)
def post_message(
    payload: ChatMessageIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation, messages = handle_turn(
        db,
        current_user,
        payload.content,
        payload.conversation_id,
        payload.project_id,
        payload.media_asset_id,
    )
    return ChatTurnOut(
        conversation_id=conversation.id,
        messages=[ChatMessageOut.model_validate(m) for m in messages],
    )


@router.get("/conversations/{conversation_id}/messages", response_model=list[ChatMessageOut])
def get_conversation_messages(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = db.get(ChatConversation, conversation_id)
    if conversation is None or conversation.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Percakapan tidak ditemukan.")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    return [ChatMessageOut.model_validate(m) for m in messages]
