"""The motion preset catalog — code-defined (not a DB table), same reasoning as
`video_render.PLATFORM_DURATION_LIMITS_SECONDS`. Add a new preset by adding a module
next to `editorial_newspaper.py` (with its own `SPEC` + `build()`) and registering both
below.
"""
from app.services.motion_presets import editorial_newspaper
from app.services.motion_presets.base import MotionPresetSpec

MOTION_PRESETS: dict[str, MotionPresetSpec] = {
    editorial_newspaper.SPEC.id: editorial_newspaper.SPEC,
}

_BUILDERS = {
    editorial_newspaper.SPEC.id: editorial_newspaper.build,
}


def get_builder(preset_id: str):
    return _BUILDERS.get(preset_id)
