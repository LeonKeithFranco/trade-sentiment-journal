class AuthError(Exception):
    """Base error for all auth errors."""


class UserAlreadyExistsError(AuthError):
    """The user already exists in the database."""
