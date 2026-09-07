from pydantic import BaseModel


class MotionPresetOut(BaseModel):
    id: str
    name: str
    description: str
    aspect_ratio: str
    min_duration_seconds: float
    max_duration_seconds: float
