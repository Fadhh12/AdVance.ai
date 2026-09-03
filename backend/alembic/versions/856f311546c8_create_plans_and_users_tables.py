"""create plans and users tables

Revision ID: 856f311546c8
Revises:
Create Date: 2026-09-04 00:34:26.912709

"""
from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "856f311546c8"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "plans",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("ai_generation_quota", sa.Integer(), nullable=False),
        sa.Column("connected_accounts_limit", sa.Integer(), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("period", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("google_id", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("plan_id", sa.Uuid(), nullable=True),
        sa.Column("ai_generation_used", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("google_id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"])

    # Seed a default Free plan so new registrations have somewhere to land
    # (Phase 7 adds the real billing/plan-management UI on top of this table).
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
                "id": "00000000-0000-0000-0000-000000000001",
                "name": "Free",
                "ai_generation_quota": 5,
                "connected_accounts_limit": 1,
                "price": 0,
                "period": "monthly",
                "created_at": datetime.now(UTC),
            }
        ],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_table("plans")
