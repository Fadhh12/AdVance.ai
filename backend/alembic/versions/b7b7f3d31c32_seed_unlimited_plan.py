"""seed unlimited plan

Revision ID: b7b7f3d31c32
Revises: 1038d694248b
Create Date: 2026-09-07 04:20:00.000000

"""
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7b7f3d31c32"
down_revision: str | None = "1038d694248b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Phase 6R: an "Unlimited" plan for the app owner's own account — assigned
    # automatically on register/Google login when the email matches OWNER_EMAIL in
    # .env (see app/api/auth.py), never self-serve. Everyone else still lands on
    # "Free" (seeded in 856f311546c8) or a guest account (same Free plan).
    plans = sa.table(
        "plans",
        sa.column("id", sa.Uuid()),
        sa.column("name", sa.String()),
        sa.column("ai_generation_quota", sa.Integer()),
        sa.column("connected_accounts_limit", sa.Integer()),
        sa.column("price", sa.Integer()),
        sa.column("period", sa.String()),
        sa.column("created_at", sa.DateTime()),
    )
    op.bulk_insert(
        plans,
        [
            {
                "id": str(uuid.uuid4()),
                "name": "Unlimited",
                "ai_generation_quota": 1_000_000,
                "connected_accounts_limit": 100,
                "price": 0,
                "period": "monthly",
                "created_at": datetime.now(UTC),
            }
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM plans WHERE name = 'Unlimited'")
