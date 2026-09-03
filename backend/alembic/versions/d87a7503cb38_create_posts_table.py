"""create posts table

Revision ID: d87a7503cb38
Revises: 470511c8fd3d
Create Date: 2026-09-04 01:27:58.112010

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d87a7503cb38"
down_revision: str | None = "470511c8fd3d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "posts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("platform", sa.String(length=20), nullable=False),
        sa.Column("export_status", sa.String(length=20), nullable=True),
        sa.Column("export_error_message", sa.Text(), nullable=True),
        sa.Column("video_key", sa.String(length=500), nullable=True),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["content_projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_posts_project_id"), "posts", ["project_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_posts_project_id"), table_name="posts")
    op.drop_table("posts")
