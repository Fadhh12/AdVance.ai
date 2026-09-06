"""Template gallery (Phase 6R): a global catalog of pre-made "starting point" style
presets the user can pick before generating (Dreamina-style template picker). Not
per-user — every active row is visible to everyone, same as a public catalog. Picking
one only prefills the Generate panel's existing `prompt`/`mode` fields (see
`app/api/templates.py`) — it never adds new fields to `GenerateVideoRequest`.
"""
import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    mode: Mapped[str] = mapped_column(String(20))  # product_ad | affiliate
    prompt_preset: Mapped[str] = mapped_column(Text)  # prefills Generate panel's prompt
    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
