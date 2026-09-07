"""Shared type for the motion preset catalog. A preset is render logic (an ffmpeg
recipe), not user data — the catalog lives in code (`registry.py`), not a DB table.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class MotionPresetSpec:
    id: str
    name: str
    description: str
    aspect_ratio: str
    min_duration_seconds: float
    max_duration_seconds: float
