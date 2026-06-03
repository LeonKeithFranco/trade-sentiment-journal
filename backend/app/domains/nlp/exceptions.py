class NLPError(Exception):
    """Base error for all NLP errors."""


class EmptyTextError(NLPError):
    """Attempted to pass and empty sequence to the model."""
