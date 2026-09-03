import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GenerateVideoRequest(BaseModel):
    source_asset_id: uuid.UUID
    prompt: str | None = None  # gaya referensi opsional


class AIJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: str
    status: str
    provider: str
    result_url: str | None
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None
