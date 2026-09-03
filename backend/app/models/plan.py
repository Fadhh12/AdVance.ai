"""Subscription plan / quota definition (SDD §3.3: subscriptions/plans)."""
import uuid
from datetime import UTC, datetime

from sqlalchemy import Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    ai_generation_quota: Mapped[int] = mapped_column(Integer)
    connected_accounts_limit: Mapped[int] = mapped_column(Integer)
    price: Mapped[int] = mapped_column(Integer)  # smallest currency unit (Rupiah, no decimals)
    period: Mapped[str] = mapped_column(String(20), default="monthly")  # monthly/yearly
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    users: Mapped[list["User"]] = relationship(back_populates="plan")  # noqa: F821
