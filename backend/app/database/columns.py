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
