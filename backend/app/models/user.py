"""User account (SDD §3.3: users). `password_hash` is nullable — a user who only ever
signs in via Google OAuth never gets one.
"""
import uuid
from datetime import UTC, datetime

from sqlalchemy import ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(120))
    plan_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("plans.id"), nullable=True)

    # FR-11 quota tracking dasar — detail per-action log ada di `usage_logs` (Phase 7).
    ai_generation_used: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    plan: Mapped["Plan | None"] = relationship(back_populates="users")  # noqa: F821
