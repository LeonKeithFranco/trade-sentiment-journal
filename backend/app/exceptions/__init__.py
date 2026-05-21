from app.database.exceptions import DatabaseError
from app.domains.auth.exceptions import (
    UserAlreadyExistsError,
    UserInvalidCredentialsError,
)

__all__ = [
    "DatabaseError",
    "UserAlreadyExistsError",
    "UserInvalidCredentialsError",
]
