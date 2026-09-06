import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    mode: str
    prompt_preset: str
    thumbnail_url: str | None
    created_at: datetime
