import uuid
from typing import Annotated

from fastapi import Depends

from app.database import DbDependency
from app.database.repository import Repository
from app.models import Trade

type MaybeTrade = Trade | None


class TradeRepository(Repository[Trade]):
    """Data-access layer for Trade records.

    Attributes:
        db: The underlying async SQLAlchemy session.
    """

    def __init__(self, db: DbDependency) -> None:
        """Initialize the repository with a database session.

        Args:
            db: An async SQLAlchemy session, provided by FastAPI's dependency
                injection via get_db.
        """
        super().__init__(db)

    async def insert_trade(self, **create_info) -> Trade:
        """Create a new trade record.

        Args:
            **create_info: Column values to set on the new trade.

        Returns:
            Trade: The newly created trade.
        """
        return await self.insert_into_table(Trade, **create_info)

    async def get_trade_by_public_id_for_user(
        self, trade_public_id: uuid.UUID, user_id: int
    ) -> MaybeTrade:
        """Look up a trade by public ID, scoped to a specific user.

        Args:
            trade_public_id: The public UUID of the trade to search for.
            user_id: The ID of the user the trade must belong to.

        Returns:
            Trade: The matching trade, or None if no trade with that public
                ID exists for the user.
        """
        return await self.get_from_table_by(
            Trade, Trade.public_id == trade_public_id, Trade.user_id == user_id
        )

    async def get_all_trades_by_user_id(self, user_id: int) -> list[Trade]:
        """Fetch all trades belonging to a user.

        Args:
            user_id: The ID of the user whose trades to fetch.

        Returns:
            list[Trade]: All trades belonging to the user.
        """
        return await self.get_all_from_table(Trade, Trade.user_id == user_id)

    async def delete_trade_by_public_id_for_user(
        self, trade_public_id: uuid.UUID, user_id: int
    ) -> int:
        """Delete a trade by public ID, scoped to a specific user.

        Args:
            trade_public_id: The public UUID of the trade to delete.
            user_id: The ID of the user the trade must belong to.

        Returns:
            int: The number of rows deleted (0 or 1).
        """
        return await self.delete_from_table_by(
            Trade, Trade.public_id == trade_public_id, Trade.user_id == user_id
        )

    async def update_trade(
        self,
        trade: Trade,
        **update_info,
    ) -> Trade:
        """Update an existing trade's attributes and persist the change.

        Args:
            trade: The trade instance to update.
            **update_info: Column values to set on the trade.

        Returns:
            Trade: The updated trade.
        """
        return await self.update_record(trade, **update_info)


TradeRepoDependency = Annotated[TradeRepository, Depends(TradeRepository)]
