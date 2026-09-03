"""create content_projects table

Revision ID: 470511c8fd3d
Revises: 61abd86fc8b2
Create Date: 2026-09-04 01:12:31.799345

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "470511c8fd3d"
down_revision: str | None = "61abd86fc8b2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "content_projects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("mode", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("source_job_id", sa.Uuid(), nullable=False),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("music_track", sa.String(length=100), nullable=True),
        sa.Column("trim_start_seconds", sa.Float(), nullable=True),
        sa.Column("trim_end_seconds", sa.Float(), nullable=True),
        sa.Column("render_status", sa.String(length=20), nullable=True),
        sa.Column("render_error_message", sa.Text(), nullable=True),
        sa.Column("final_video_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["source_job_id"], ["ai_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_content_projects_user_id"), "content_projects", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_content_projects_user_id"), table_name="content_projects")
    op.drop_table("content_projects")
