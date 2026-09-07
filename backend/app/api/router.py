"""Aggregates all domain routers (SDD §3.5: routers per domain — auth, media, ai, projects,
posts). Each phase adds its router here as it's built; keep this file as the single place
that wires them into the app.
"""
from fastapi import APIRouter

from app.api import ai, auth, chat, health, media, motion_presets, posts, projects, templates

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(media.router, prefix="/media", tags=["media"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(
    motion_presets.router, prefix="/motion-presets", tags=["motion-presets"]
)
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
# Phase 3: api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
# Phase 4: api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
# Phase 5: api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
