from typing import Annotated

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column

UserIDColumn = Annotated[
    int,
    mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    ),
]

TradeIDColumn = Annotated[
    int,
    mapped_column(
        ForeignKey("trades.id", ondelete="CASCADE"),
        index=True,
    ),
]

JournalEntryIDColumn = Annotated[
    int,
    mapped_column(
        ForeignKey("journal_entries.id", ondelete="CASCADE"),
        unique=True,
    ),
]
