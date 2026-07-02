from pydantic import BaseModel, Field

from app.domains.nlp.constants import SentimentEnum


class NLPRequest(BaseModel):
    """Pydantic request model for the POST /analyze endpoint.

    Attributes:
        text: The text to run sentiment analysis on.
    """

    text: str = Field(max_length=4096)


class NLPResponse(BaseModel):
    """Pydantic response model for the POST /analyze endpoint.

    Attributes:
        sentiment: The predicted sentiment classification.
        confidence: The model's confidence in the predicted sentiment,
            between 0.0 and 1.0.
    """

    sentiment: SentimentEnum
    confidence: float = Field(ge=0, le=1)
