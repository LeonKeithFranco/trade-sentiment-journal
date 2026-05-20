from app.database.exceptions import DatabaseError
from app.domains.auth.exceptions import UserAlreadyExistsError

__all__ = [
    "DatabaseError",
    "UserAlreadyExistsError",
]
