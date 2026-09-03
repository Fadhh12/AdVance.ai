"""Uploaded raw photo/video (SDD §3.3: media_assets). `file_url` stores the S3 **object
key**, not a URL — the bucket is private (SDD §3.6). A fresh signed URL is generated on
read (see app/services/storage.py) and never persisted.
"""
import uuid
from datetime import UTC, datetime

from sqlalchemy import ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    type: Mapped[str] = mapped_column(String(20))  # "photo" | "video_raw"
    file_url: Mapped[str] = mapped_column(String(500))  # S3 object key
    original_filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(Integer)
    uploaded_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
