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
from app.main import app
from app.models.base import Base, get_db
from app.models.plan import Plan
from app.workers.celery_app import celery_app

# No Redis in this environment yet (see PROGRESS.md) — eager mode runs `.delay()`
# synchronously in-process instead of needing a real broker, so the task code path
# still gets exercised for real by the test suite.
celery_app.conf.update(task_always_eager=True, task_eager_propagates=True)


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Mirrors the "Free" plan seeded by the first Alembic migration in real Postgres.
    with TestingSessionLocal() as seed_session:
        seed_session.add(
            Plan(name="Free", ai_generation_quota=5, connected_accounts_limit=1, price=0)
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
