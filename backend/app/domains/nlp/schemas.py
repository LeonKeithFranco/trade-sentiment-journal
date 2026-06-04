from pydantic import BaseModel, Field

from app.domains.nlp.constants import SentimentEnum


class NLPRequest(BaseModel):
    text: str = Field(max_length=4096)


class NLPResponse(BaseModel):
    sentiment: SentimentEnum
    confidence: float = Field(ge=0, le=1)
