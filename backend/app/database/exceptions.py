class DatabaseError(RuntimeError):
    """There is an issue when trying to use the database."""


class ClosedAtBeforeOpenedAtError(DatabaseError):
    """There is an attempt to try to set closed_at datetime to before opened_at datetime and vice versa."""
