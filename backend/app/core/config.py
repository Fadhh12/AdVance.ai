"""App-wide settings, loaded from environment / .env (SDD §3.5: app/core)."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- App ---
    app_name: str = "adVance.AI"
    env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-to-a-random-64-char-string"

    # --- Database ---
    database_url: str = (
        "postgresql+psycopg2://advance:advance_dev_password@localhost:5432/advance_ai"
    )

    # --- Redis / Celery ---
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # --- Object storage (S3-compatible) ---
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "advance_minio"
    s3_secret_key: str = "advance_minio_dev_password"
    s3_bucket_name: str = "media-assets"
    s3_region: str = "us-east-1"
    s3_use_path_style: bool = True

    # --- Auth ---
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""

    # --- AI providers (Phase 3) ---
    ai_video_provider: str = "mock"
    ai_video_provider_api_key: str = ""

    # --- Social platform apps (Phase 6, not usable yet) ---
    meta_app_id: str = ""
    meta_app_secret: str = ""
    tiktok_client_key: str = ""
    tiktok_client_secret: str = ""
    youtube_oauth_client_id: str = ""
    youtube_oauth_client_secret: str = ""

    # --- CORS ---
    frontend_origin: str = "http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
