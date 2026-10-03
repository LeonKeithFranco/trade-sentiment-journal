from fastapi import APIRouter

from app.domains.nlp.schemas import NLPRequest, NLPResponse
from app.domains.nlp.service import NLPServiceDependency
from app.security import CurrentUserDependency

router = APIRouter(prefix="/analyze", tags=["nlp"])


@router.post("", response_model=NLPResponse)
async def analyze(
    nlp_request: NLPRequest,
    current_user: CurrentUserDependency,  # used to make sure API caller is registered user
    nlp_service: NLPServiceDependency,
) -> NLPResponse:
    """Run sentiment analysis on an arbitrary piece of text.

    Args:
        nlp_request: The request body containing the text to analyze.
        current_user: The authenticated user making the request, used only
            to enforce that the caller is a registered user.
        nlp_service: The injected NLPService instance.

    Returns:
        NLPResponse: The predicted sentiment classification and confidence
            score.
    """
    return await nlp_service.inference(nlp_request.text)
