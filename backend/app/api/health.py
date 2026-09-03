"""Liveness/readiness endpoint — used by CI, Docker healthcheck, and manual verification."""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return {"status": "ok"}
