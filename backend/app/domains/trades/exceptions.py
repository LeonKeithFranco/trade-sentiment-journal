class TradeError(Exception):
    """Base error for all trade errors."""


class TradeDoesNotExistError(TradeError):
    """Trade does not exist in the database."""
