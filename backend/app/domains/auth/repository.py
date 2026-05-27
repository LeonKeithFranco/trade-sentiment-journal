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
    def __init__(self, db: DbDependency) -> None:
        super().__init__(db)

    async def _get_user_by(self, *where_clauses: ColumnElement[bool]) -> MaybeUser:
        return await self.get_from_table_by(User, *where_clauses)

    async def get_user_by_email(self, email: str) -> MaybeUser:
        return await self._get_user_by(User.email == email)

    async def get_user_by_public_id(self, public_id: uuid.UUID) -> MaybeUser:
        return await self._get_user_by(User.public_id == public_id)

    async def insert_user(self, **create_info) -> User:
        return await self.insert_into_table(User, **create_info)


UserRepoDependency = Annotated[UserRepository, Depends(UserRepository)]


class RefreshTokenRepository(Repository[RefreshToken]):
    def __init__(self, db: DbDependency) -> None:
        super().__init__(db)

    async def get_refresh_token(self, token: str) -> MaybeRefreshToken:
        return await self.get_from_table_by(
            RefreshToken,
            RefreshToken.token == token,
            options=[selectinload(RefreshToken.user)],
        )

    async def revoke_refresh_token(self, token: str) -> None:
        token_record = await self.get_from_table_by(
            RefreshToken, RefreshToken.token == token
        )
        await self.update_record(cast(RefreshToken, token_record), revoked=True)

    async def insert_refresh_token(
        self, user_id: int, refresh_token: str, expire: datetime
    ) -> RefreshToken:
        return await self.insert_into_table(
            RefreshToken, token=refresh_token, expires_on=expire, user_id=user_id
        )


RefreshTokenRepoDependency = Annotated[
    RefreshTokenRepository, Depends(RefreshTokenRepository)
]
