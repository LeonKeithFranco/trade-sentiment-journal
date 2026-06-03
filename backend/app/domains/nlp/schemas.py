from pydantic import BaseModel, Field


class NLPRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4096)


class NLPResponse(BaseModel):
    sentiment: str
    confidence: float
