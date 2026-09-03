import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

Mode = Literal["product_ad", "affiliate"]


class ContentProjectCreate(BaseModel):
    title: str
    mode: Mode
    source_job_id: uuid.UUID


class ContentProjectUpdate(BaseModel):
    """PATCH semantics — every field optional, only what's sent gets changed."""

    title: str | None = None
    caption: str | None = None
    music_track: str | None = None
    trim_start_seconds: float | None = None
    trim_end_seconds: float | None = None


class ContentProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    mode: str
    status: str
    caption: str | None
    music_track: str | None
    trim_start_seconds: float | None
    trim_end_seconds: float | None
    render_status: str | None
    render_error_message: str | None
    source_video_url: str  # resolved from the source AIJob, not a DB column
    final_video_url: str | None  # signed, resolved at read time if present
    created_at: datetime
    updated_at: datetime
