class AuthError(Exception):
    """Base error for all auth errors."""


class UserAlreadyExists(AuthError):
    """The user already exists in the database."""
