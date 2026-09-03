"""FastAPI entrypoint (SDD §3.5)."""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger("advance_ai")

app = FastAPI(title=settings.app_name, debug=settings.debug)


class CatchUnhandledErrorsMiddleware(BaseHTTPMiddleware):
    """Turns an unhandled exception (e.g. Postgres unreachable) into a normal JSON 500
    instead of letting it reach Starlette's ServerErrorMiddleware.

    `@app.exception_handler(Exception)` looks like the obvious fix but Starlette special-
    cases handlers registered for `Exception`/500: it wires them into ServerErrorMiddleware,
    which sits *outside* CORSMiddleware in the stack, so no CORS headers ever reach the
    error response — the browser can't read it and fetch() reports a bare "Failed to
    fetch" with no status/body. Catching it here, in ordinary middleware placed *inside*
    CORSMiddleware (registered before it, see add_middleware order below), keeps the error
    response inside CORS's wrapped `send` so headers get added normally."""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception:
            logger.exception("Unhandled error on %s %s", request.method, request.url.path)
            detail = (
                "Internal server error — cek log backend untuk detail."
                if not settings.debug
                else "Internal server error. Cek terminal backend untuk traceback lengkap."
            )
            return JSONResponse(status_code=500, content={"detail": detail})


# Registered before CORSMiddleware so it ends up *inside* it in the middleware stack
# (each add_middleware call wraps closer to the client) — see class docstring above.
app.add_middleware(CatchUnhandledErrorsMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
