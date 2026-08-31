class AuthError(Exception):
    """Base error for all auth errors."""


class UserAlreadyExistsError(AuthError):
    """The user already exists in the database."""


class UserInvalidCredentialsError(AuthError):
    """Either email or password is incorrect."""
