from pydantic import BaseModel, Field

from app.domains.nlp.constants import SentimentEnum


class NLPRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4096)


class NLPResponse(BaseModel):
    sentiment: SentimentEnum
    confidence: float
