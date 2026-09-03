"""Import every model module here so Base.metadata sees all tables (Alembic autogenerate
and `Base.metadata.create_all` both rely on this).
"""
from app.models.ai_job import AIJob  # noqa: F401
from app.models.media_asset import MediaAsset  # noqa: F401
from app.models.plan import Plan  # noqa: F401
from app.models.user import User  # noqa: F401
