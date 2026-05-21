from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select

from app.database import DbDependency
from app.database.repository import Repository
from app.domains.auth.models import RefreshToken, User

type MaybeUser = User | None


class AuthRepository(Repository):
    def __init__(self, db: DbDependency) -> None:
        super().__init__(db)

    async def get_user_by_email(self, email: str) -> MaybeUser:
        query = select(User).where(User.email == email)
        results = await self.db.execute(query)
        user = results.scalar_one_or_none()

        return user

    async def insert_user(self, email: str, hashed_password: str) -> User:
        new_user = User()
        new_user.email = email
        new_user.hashed_password = hashed_password

        self.db.add(new_user)
        await self.db.flush()
        await self.db.refresh(new_user)

        return new_user

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


AuthRepoDependency = Annotated[AuthRepository, Depends(AuthRepository)]
