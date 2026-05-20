from sqlalchemy import select

from app.auth.models import User
from app.database import DbDependency
from app.database.repository import Repository

type MaybeUser = User | None


class AuthRepository(Repository):
    def __init__(self, db: DbDependency) -> None:
        super().__init__(db)

    async def get_user_by_email(self, email: str) -> MaybeUser:
        query = select(User).where(User.email == email)
        results = await self.db.execute(query)
        user = results.scalar_one_or_none()

        return user
