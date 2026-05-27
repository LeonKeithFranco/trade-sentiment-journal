class TradeError(Exception):
    """Base error for all trade errors."""


class TradeDoesNotExistError(TradeError):
    """Trade does not exist in the database."""


class ClosedAtBeforeOpenedAtError(TradeError):
    """There is an attempt to try to set closed_at datetime to before opened_at datetime and vice versa."""
