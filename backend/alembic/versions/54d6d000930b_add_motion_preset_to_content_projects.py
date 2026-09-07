"""add motion_preset to content_projects

Revision ID: 54d6d000930b
Revises: b7b7f3d31c32
Create Date: 2026-09-07 21:13:42.952061

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "54d6d000930b"
down_revision: str | None = "b7b7f3d31c32"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # NOTE: autogenerate also flagged an unrelated users.email index/constraint drift
    # (pre-existing, out of scope for this migration — same call made in
    # 8b124fa99bc5_create_templates_table.py) — deliberately not included here.
    op.add_column(
        "content_projects", sa.Column("motion_preset", sa.String(length=50), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("content_projects", "motion_preset")
