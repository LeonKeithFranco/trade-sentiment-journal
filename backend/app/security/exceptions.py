class TokenError(Exception):
    """Base error for all token errors."""


class InvalidAccessTokenError(TokenError):
    """Access token is invalid."""

    def __init__(self, reason: str = "") -> None:
        self.reason: str = reason
        super().__init__(reason)
