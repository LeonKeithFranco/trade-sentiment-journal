"""increase precision on trade values

Revision ID: 684e7ed6c7d0
Revises: abe4018d751e
Create Date: 2026-10-05 10:28:13.119648

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "684e7ed6c7d0"
down_revision: Union[str, Sequence[str], None] = "abe4018d751e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "trades",
        "position_size",
        existing_type=sa.NUMERIC(precision=12, scale=2),
        type_=sa.Numeric(precision=16, scale=6),
        existing_nullable=False,
    )
    op.alter_column(
        "trades",
        "entry_price",
        existing_type=sa.NUMERIC(precision=12, scale=2),
        type_=sa.Numeric(precision=16, scale=6),
        existing_nullable=False,
    )
    op.alter_column(
        "trades",
        "exit_price",
        existing_type=sa.NUMERIC(precision=12, scale=2),
        type_=sa.Numeric(precision=16, scale=6),
        existing_nullable=True,
    )
    op.alter_column(
        "trades",
        "profit_and_loss",
        existing_type=sa.NUMERIC(precision=12, scale=2),
        type_=sa.Numeric(precision=16, scale=6),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "trades",
        "profit_and_loss",
        existing_type=sa.Numeric(precision=16, scale=6),
        type_=sa.NUMERIC(precision=12, scale=2),
        existing_nullable=True,
    )
    op.alter_column(
        "trades",
        "exit_price",
        existing_type=sa.Numeric(precision=16, scale=6),
        type_=sa.NUMERIC(precision=12, scale=2),
        existing_nullable=True,
    )
    op.alter_column(
        "trades",
        "entry_price",
        existing_type=sa.Numeric(precision=16, scale=6),
        type_=sa.NUMERIC(precision=12, scale=2),
        existing_nullable=False,
    )
    op.alter_column(
        "trades",
        "position_size",
        existing_type=sa.Numeric(precision=16, scale=6),
        type_=sa.NUMERIC(precision=12, scale=2),
        existing_nullable=False,
    )
