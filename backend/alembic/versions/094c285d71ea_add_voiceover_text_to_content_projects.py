"""add voiceover_text to content_projects

Revision ID: 094c285d71ea
Revises: 54d6d000930b
Create Date: 2026-09-08 13:40:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "094c285d71ea"
down_revision: str | None = "54d6d000930b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "content_projects", sa.Column("voiceover_text", sa.Text(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("content_projects", "voiceover_text")
