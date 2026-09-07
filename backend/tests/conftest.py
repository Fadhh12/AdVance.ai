"""Shared test fixtures. Uses an in-memory SQLite DB (via dependency override) so the
suite runs without a live Postgres — real Postgres-specific behavior still needs manual
verification via `alembic upgrade head` once Docker/Postgres is available (see PROGRESS.md).
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 — registers all tables on Base.metadata
import app.models.base as models_base
from app.core.config import get_settings
from app.main import app
from app.models.base import Base, get_db
from app.models.plan import Plan
from app.workers.celery_app import celery_app

# No Redis in this environment yet (see PROGRESS.md) — eager mode runs `.delay()`
# synchronously in-process instead of needing a real broker, so the task code path
# still gets exercised for real by the test suite.
celery_app.conf.update(task_always_eager=True, task_eager_propagates=True)


@pytest.fixture(autouse=True)
def _force_mock_providers(monkeypatch):
    """Settings loads the developer's real local `.env` (pydantic-settings does this
    regardless of pytest) — the suite must never depend on whatever real provider/API
    key happens to be configured there for actual local usage. Force every AI provider
    back to "mock" for the duration of each test; individual tests can still
    monkeypatch a specific provider name on top of this to test factory fail-loud
    paths (e.g. test_llm_providers.py's "openai"/"anthropic" cases).
    """
    settings = get_settings()
    monkeypatch.setattr(settings, "ai_video_provider", "mock")
    monkeypatch.setattr(settings, "ai_llm_provider", "mock")
    monkeypatch.setattr(settings, "ai_image_provider", "mock")
    monkeypatch.setattr(settings, "ai_voiceover_provider", "mock")
    # Same reasoning: never let a real local N8N_WEBHOOK_URL cause tests to fire real
    # HTTP calls out to an n8n instance (Phase 6R-10) — force disabled by default,
    # individual tests can still monkeypatch it back on to test the notify path itself.
    monkeypatch.setattr(settings, "n8n_webhook_url", "")


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Mirrors the "Free" + "Unlimited" plans seeded by the Alembic migrations in real
    # Postgres (856f311546c8, b7b7f3d31c32 — Phase 6R owner account).
    with TestingSessionLocal() as seed_session:
        seed_session.add_all(
            [
                Plan(name="Free", ai_generation_quota=5, connected_accounts_limit=1, price=0),
                Plan(
                    name="Unlimited",
                    ai_generation_quota=1_000_000,
                    connected_accounts_limit=100,
                    price=0,
                ),
            ]
        )
        seed_session.commit()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Celery tasks open their own session via `models_base.SessionLocal()` (not the
    # FastAPI dependency) — point that at the same test engine too, so a task run
    # eagerly inside a request sees the request's own data.
    original_session_local = models_base.SessionLocal
    models_base.SessionLocal = TestingSessionLocal

    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    models_base.SessionLocal = original_session_local
