class NLPError(Exception):
    """Base error for all NLP errors."""


class EmptyTextError(NLPError):
    """Attempted to pass an empty sequence to the model."""
