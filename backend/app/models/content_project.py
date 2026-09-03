"""Lightweight editor project (SDD §3.3: content_projects), extended with the fields
FR-05's "trim, caption, ganti musik" and the Phase 4 ffmpeg render worker actually need
— SDD's base column list (title/mode/status/final_video_url) doesn't spell these out.
`status` stays limited to SDD's own values (draft/ready/scheduled/published); the render
worker's own in-flight state lives in `render_status` instead of overloading `status`.

Single-clip only for now: `source_job_id` points at exactly one `ai_jobs` row, so there
is no multi-clip "reorder" to support yet (see PROGRESS.md Phase 4).
"""
import uuid
from datetime import UTC, datetime

from sqlalchemy import Float, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ContentProject(Base):
    __tablename__ = "content_projects"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    mode: Mapped[str] = mapped_column(String(20))  # product_ad | affiliate
    # draft | ready | scheduled | published
    status: Mapped[str] = mapped_column(String(20), default="draft")
    source_job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_jobs.id"))

    # Edit ringan (FR-05)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    music_track: Mapped[str | None] = mapped_column(String(100), nullable=True)
    trim_start_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    trim_end_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Render worker (ffmpeg) state — separate from `status` so a failed render doesn't
    # need a bespoke value squeezed into SDD's draft/ready/scheduled/published set.
    render_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    render_error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)  # S3 key

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
