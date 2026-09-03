"""Per-platform publish record (SDD §3.3: posts), scoped to Phase 5 "Publish Manual
Assist" (FR-13/FR-14) — `social_account_id`, `scheduled_at`, `published_at`,
`platform_post_id` from the full SDD schema are deferred to Phase 6, when
`social_accounts` (and real auto-publish) actually exist; adding unused columns now
would just be dead weight. `status` stays within FR-13/FR-14's manual-assist values
(manual_ready/manual_uploaded) — the scheduled/publishing/published/failed values
belong to Phase 6's real publish flow.
"""
import uuid
from datetime import UTC, datetime

from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_projects.id"), index=True)
    platform: Mapped[str] = mapped_column(String(20))  # instagram | tiktok | youtube

    # Export worker (ffmpeg crop/duration + caption adaptation) state.
    export_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    export_error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    video_key: Mapped[str | None] = mapped_column(String(500), nullable=True)  # S3 key
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)  # platform-adapted

    # manual_ready (export done, user can download/share) | manual_uploaded (user
    # self-marked as uploaded — FR-13/FR-14). Null until export succeeds.
    status: Mapped[str | None] = mapped_column(String(20), nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
