from typing import Annotated

from dl.preprocess import process_and_map_sentence
from fastapi import Depends

from app.core.model import model_inference
from app.domains.nlp.constants import SentimentEnum
from app.domains.nlp.exceptions import EmptyTextError
from app.domains.nlp.schemas import NLPResponse


class NLPService:
    """Service layer for running sentiment analysis on text."""

    async def inference(self, text: str) -> NLPResponse:
        """Run sentiment analysis on a piece of text.

        Tokenizes and maps the text to model input IDs before running
        inference.

        Args:
            text: The raw text to analyze.

        Returns:
            NLPResponse: The predicted sentiment classification and
                confidence score.

        Raises:
            EmptyTextError: If the text is empty or reduces to no tokens
                after preprocessing.
        """
        processed = process_and_map_sentence(text)

        if not processed:
            raise EmptyTextError("Text being passed to model cannot be empty")

        class_label, confidence_level = await model_inference(processed)

        return NLPResponse(
            sentiment=SentimentEnum(class_label),
            confidence=confidence_level,
        )


NLPServiceDependency = Annotated[NLPService, Depends(NLPService)]
