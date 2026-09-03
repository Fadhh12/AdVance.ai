import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

Platform = Literal["instagram", "tiktok", "youtube"]


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    platform: str
    export_status: str | None
    export_error_message: str | None
    caption: str | None
    youtube_title: str | None = None  # only set for platform == "youtube"
    video_url: str | None  # signed, resolved at read time if export succeeded
    status: str | None
    created_at: datetime
