"""Async AI job — generate video, caption, or voice-over (SDD §3.3: ai_jobs). Lifecycle:
queued -> processing -> success/failed (SRS §2.3).
"""
import uuid
from datetime import UTC, datetime

from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AIJob(Base):
    __tablename__ = "ai_jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    source_asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("media_assets.id"))
    type: Mapped[str] = mapped_column(String(20))  # generate_video | caption | voiceover
    status: Mapped[str] = mapped_column(String(20), default="queued")
    provider: Mapped[str] = mapped_column(String(50))
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
