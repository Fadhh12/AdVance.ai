"""Template gallery (Phase 6R): read-only global catalog, no per-user ownership —
picking a template only prefills the Generate panel's existing prompt/mode fields on
the frontend, nothing new is sent to `POST /ai/generate-video`.
"""
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.models.base import get_db
from app.models.template import Template
from app.models.user import User
from app.schemas.template import TemplateOut

router = APIRouter()


@router.get("", response_model=list[TemplateOut])
def list_templates(
    mode: Literal["product_ad", "affiliate"] | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    del current_user  # auth-gated like the rest of the app, but catalog isn't per-user
    query = select(Template).where(Template.is_active.is_(True))
    if mode is not None:
        query = query.where(Template.mode == mode)
    templates = db.execute(query.order_by(Template.created_at)).scalars()
    return [TemplateOut.model_validate(template) for template in templates]
