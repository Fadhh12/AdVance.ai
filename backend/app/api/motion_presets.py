"""Motion preset catalog (Phase 6R-8) — local ffmpeg-based "video-effect generator"
presets (e.g. editorial-newspaper), selectable before rendering a project. Read-only,
code-defined (services/motion_presets/registry.py), same auth-but-not-per-user pattern
as app/api/templates.py.
"""
from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.user import User
from app.schemas.motion_preset import MotionPresetOut
from app.services.motion_presets.registry import MOTION_PRESETS

router = APIRouter()


@router.get("", response_model=list[MotionPresetOut])
def list_motion_presets(current_user: User = Depends(get_current_user)):
    del current_user  # auth-gated like the rest of the app, catalog isn't per-user
    return [
        MotionPresetOut(
            id=spec.id,
            name=spec.name,
            description=spec.description,
            aspect_ratio=spec.aspect_ratio,
            min_duration_seconds=spec.min_duration_seconds,
            max_duration_seconds=spec.max_duration_seconds,
        )
        for spec in MOTION_PRESETS.values()
    ]
