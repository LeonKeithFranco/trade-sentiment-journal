import uuid
from datetime import datetime
from typing import Annotated, cast

from fastapi import Depends
from sqlalchemy import ColumnElement
from sqlalchemy.orm import selectinload

from app.database import DbDependency
from app.database.repository import Repository
from app.domains.auth.models import RefreshToken, User

type MaybeUser = User | None
type MaybeRefreshToken = RefreshToken | None


class UserRepository(Repository[User]):
    """Data-access layer for User records.

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

    async def _get_user_by(self, *where_clauses: ColumnElement[bool]) -> MaybeUser:
        """Fetch a single user matching the given clauses.

        Args:
            *where_clauses: SQLAlchemy filter conditions to apply.

        Returns:
            User: The matching user, or None if no user matches.
        """
        return await self.get_from_table_by(User, *where_clauses)

    async def get_user_by_email(self, email: str) -> MaybeUser:
        """Look up a user by email address.

        Args:
            email: The email address to search for.

        Returns:
            User: The matching user, or None if no user with that email exists.
        """
        return await self._get_user_by(User.email == email)

    async def get_user_by_public_id(self, public_id: uuid.UUID) -> MaybeUser:
        """Look up a user by public ID.

        Args:
            public_id: The public UUID to search for.

        Returns:
            User: The matching user, or None if no user with that public ID
                exists.
        """
        return await self._get_user_by(User.public_id == public_id)

    async def insert_user(self, **create_info) -> User:
        """Create a new user record.

        Args:
            **create_info: Column values to set on the new user.

        Returns:
            User: The newly created user.
        """
        return await self.insert_into_table(User, **create_info)


UserRepoDependency = Annotated[UserRepository, Depends(UserRepository)]


class RefreshTokenRepository(Repository[RefreshToken]):
    """Data-access layer for RefreshToken records.

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

    async def get_refresh_token(self, token: str) -> MaybeRefreshToken:
        """Look up a refresh token by its token string, with its user eagerly loaded.

        Args:
            token: The refresh token string to search for.

        Returns:
            RefreshToken: The matching refresh token with its user loaded, or
                None if no refresh token matches.
        """
        return await self.get_from_table_by(
            RefreshToken,
            RefreshToken.token == token,
            options=[selectinload(RefreshToken.user)],
        )

    async def revoke_refresh_token(self, token: str) -> None:
        """Mark a refresh token as revoked.

        Args:
            token: The refresh token string to revoke.
        """
        token_record = await self.get_from_table_by(
            RefreshToken, RefreshToken.token == token
        )
        await self.update_record(cast(RefreshToken, token_record), revoked=True)

    async def insert_refresh_token(
        self, user_id: int, refresh_token: str, expire: datetime
    ) -> RefreshToken:
        """Create a new refresh token record for a user.

        Args:
            user_id: The ID of the user the token is being issued to.
            refresh_token: The refresh token string.
            expire: The timestamp at which the token expires.

        Returns:
            RefreshToken: The newly created refresh token.
        """
        return await self.insert_into_table(
            RefreshToken, token=refresh_token, expires_on=expire, user_id=user_id
        )


RefreshTokenRepoDependency = Annotated[
    RefreshTokenRepository, Depends(RefreshTokenRepository)
]
