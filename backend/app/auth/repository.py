from app.database import DbDependency
from app.database.repository import Repository


class AuthRepository(Repository):
    def __init__(self, db: DbDependency) -> None:
        super().__init__(db)
