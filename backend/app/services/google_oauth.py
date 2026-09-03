"""Verifies a Google Sign-In ID token forwarded by the frontend's NextAuth Google
provider. Uses Google's `tokeninfo` endpoint (simplest correct option, no JWKS
handling needed) — fine for MVP volume; if login traffic grows, switch to verifying
the JWT locally against Google's published JWKS instead of calling out per login.
"""
import httpx

from app.core.config import get_settings

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


class GoogleTokenError(Exception):
    pass


def verify_google_id_token(id_token: str) -> dict:
    """Returns the verified claims (email, name, sub, ...) or raises GoogleTokenError."""
    settings = get_settings()
    try:
        response = httpx.get(GOOGLE_TOKENINFO_URL, params={"id_token": id_token}, timeout=10)
    except httpx.HTTPError as exc:
        raise GoogleTokenError(f"Tidak bisa menghubungi Google: {exc}") from exc

    if response.status_code != 200:
        raise GoogleTokenError("Token Google tidak valid atau kedaluwarsa.")

    claims = response.json()
    if not settings.google_oauth_client_id:
        raise GoogleTokenError(
            "GOOGLE_OAUTH_CLIENT_ID belum diisi di .env — login Google belum dikonfigurasi."
        )
    if claims.get("aud") != settings.google_oauth_client_id:
        raise GoogleTokenError("Token Google tidak dikeluarkan untuk aplikasi ini.")

    return claims
