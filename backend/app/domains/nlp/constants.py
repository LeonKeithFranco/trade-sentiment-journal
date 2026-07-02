from enum import StrEnum


class SentimentEnum(StrEnum):
    """The possible sentiment classifications produced by the sentiment model."""

    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
