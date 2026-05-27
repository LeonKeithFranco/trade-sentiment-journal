class JournalEntryError(Exception):
    """Base error for all journal entry errors."""


class JournalEntryDoesNotExistError(JournalEntryError):
    """Journal entry does not exist in the database."""
