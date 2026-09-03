import uuid
from datetime import datetime

from pydantic import BaseModel


class MediaAssetOut(BaseModel):
    id: uuid.UUID
    type: str
    original_filename: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime
    url: str  # freshly signed, not stored (see app/models/media_asset.py)
