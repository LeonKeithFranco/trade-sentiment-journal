"""add public uuid column to base
Revision ID: d095904c4fd7
Revises: e457dc488a90
Create Date: 2026-05-20 08:27:27.607012
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d095904c4fd7"
down_revision: Union[str, Sequence[str], None] = "e457dc488a90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column(
            "public_id",
            sa.Uuid(),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
    )
    op.create_unique_constraint("uq_users_public_id", "users", ["public_id"])
    op.alter_column("users", "public_id", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_users_public_id", "users", type_="unique")
    op.drop_column("users", "public_id")
