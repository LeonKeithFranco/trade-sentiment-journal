from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import ColumnElement, select

from app.database import DbDependency
from app.database.repository import Repository
from app.domains.auth.models import RefreshToken, User

type MaybeUser = User | None


class UserRepository(Repository):
    def __init__(self, db: DbDependency) -> None:
        super().__init__(db)

    async def _get_user_by(self, where_clause: ColumnElement[bool]) -> MaybeUser:
        query = select(User).where(where_clause)
        results = await self.db.execute(query)

        return results.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> MaybeUser:
        return await self._get_user_by(User.email == email)

    async def insert_user(self, email: str, hashed_password: str) -> User:
        new_user = User()
        new_user.email = email
        new_user.hashed_password = hashed_password

        self.db.add(new_user)
        await self.db.flush()
        await self.db.refresh(new_user)

        return new_user


UserRepoDependency = Annotated[UserRepository, Depends(UserRepository)]


class RefreshTokenRepository(Repository):
    def __init__(self, db: DbDependency) -> None:
        super().__init__(db)

    async def insert_refresh_token(
        self, user_id: int, refresh_token: str, expire: datetime
    ) -> RefreshToken:
        # don't forget to flush and refresh
        new_refresh_token = RefreshToken()
        new_refresh_token.token = refresh_token
        new_refresh_token.expires_on = expire
        new_refresh_token.user_id = user_id

        self.db.add(new_refresh_token)
        await self.db.flush()
        await self.db.refresh(new_refresh_token)

        return new_refresh_token


RefreshTokenRepoDependency = Annotated[
    RefreshTokenRepository, Depends(RefreshTokenRepository)
]
