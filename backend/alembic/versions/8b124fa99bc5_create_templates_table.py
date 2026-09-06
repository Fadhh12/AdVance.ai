"""create templates table

Revision ID: 8b124fa99bc5
Revises: d87a7503cb38
Create Date: 2026-09-07 03:46:14.029980

"""
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8b124fa99bc5"
down_revision: str | None = "d87a7503cb38"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "templates",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("mode", sa.String(length=20), nullable=False),
        sa.Column("prompt_preset", sa.Text(), nullable=False),
        sa.Column("thumbnail_url", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Seed a starter catalog (Phase 6R template gallery) — names/preset prompts are
    # editable later directly in the table; no admin UI for this yet.
    templates = sa.table(
        "templates",
        sa.column("id", sa.Uuid()),
        sa.column("name", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("mode", sa.String()),
        sa.column("prompt_preset", sa.Text()),
        sa.column("thumbnail_url", sa.String()),
        sa.column("is_active", sa.Boolean()),
        sa.column("created_at", sa.DateTime()),
    )
    now = datetime.now(UTC)
    op.bulk_insert(
        templates,
        [
            {
                "id": str(uuid.uuid4()),
                "name": "Unboxing Produk",
                "description": "Gaya unboxing — close-up tangan membuka kemasan.",
                "mode": "product_ad",
                "prompt_preset": (
                    "gaya unboxing, close-up tangan membuka kemasan, pencahayaan natural"
                ),
                "thumbnail_url": None,
                "is_active": True,
                "created_at": now,
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Testimoni Pelanggan",
                "description": "Gaya testimoni to-camera dengan nada personal.",
                "mode": "affiliate",
                "prompt_preset": (
                    "gaya testimoni to-camera, latar rumah/kamar, nada personal"
                ),
                "thumbnail_url": None,
                "is_active": True,
                "created_at": now,
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Before/After",
                "description": "Transisi cepat menyorot hasil pemakaian produk.",
                "mode": "product_ad",
                "prompt_preset": "split before-after, transisi cepat, fokus hasil produk",
                "thumbnail_url": None,
                "is_active": True,
                "created_at": now,
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Demo Produk Close-up",
                "description": "Detail produk close-up dengan latar studio minimalis.",
                "mode": "product_ad",
                "prompt_preset": "close-up detail produk, latar studio minimalis",
                "thumbnail_url": None,
                "is_active": True,
                "created_at": now,
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("templates")
