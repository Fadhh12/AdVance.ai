"""Domain exceptions raised by services in `app/services/*_service.py`. Kept separate
from `HTTPException` so a service function has exactly one caller-agnostic way to fail
— the FastAPI router translates these to HTTP responses, and the AI chat agent's tools
(Phase 6R) translate the same exceptions to a plain chat reply, without either caller
needing to know about the other.
"""


class MediaNotFoundError(Exception):
    """Referenced MediaAsset doesn't exist or isn't owned by the current user."""


class QuotaExceededError(Exception):
    """User has used up their plan's AI generation quota (SRS §2.2)."""


class JobNotFoundError(Exception):
    """Referenced AIJob doesn't exist or isn't owned by the current user."""


class JobNotReadyError(Exception):
    """Referenced AIJob hasn't finished successfully yet — nothing to build on."""


class ProjectNotFoundError(Exception):
    """Referenced ContentProject doesn't exist or isn't owned by the current user."""


class RenderNotReadyError(Exception):
    """Project hasn't been rendered successfully yet — nothing to export."""


class TemplateNotFoundError(Exception):
    """Referenced Template doesn't exist or isn't active."""


class GenerationFailedError(Exception):
    """An AI skill (image/voiceover generation, Phase 6R) failed or got bad input —
    distinct from the video pipeline's own quota/job errors above.
    """
