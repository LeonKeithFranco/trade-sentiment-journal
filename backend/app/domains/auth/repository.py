from typing import Annotated

from fastapi import Depends
from sqlalchemy import select

from app.database import DbDependency
from app.database.repository import Repository
from app.models import User

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


AuthRepoDependency = Annotated[AuthRepository, Depends(AuthRepository)]
