"""allow confidence of 1.0

Revision ID: abe4018d751e
Revises: aa4f39513004
Create Date: 2026-10-05 09:57:26.361054

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "abe4018d751e"
down_revision: Union[str, Sequence[str], None] = "aa4f39513004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("check_confidence_range", "sentiment_analysis", type_="check")
    op.create_check_constraint(
        "check_confidence_range",
        "sentiment_analysis",
        "confidence > 0.0 AND confidence <= 1.0",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("check_confidence_range", "sentiment_analysis", type_="check")
    op.create_check_constraint(
        "check_confidence_range",
        "sentiment_analysis",
        "confidence > 0.0 AND confidence < 1.0",
    )
