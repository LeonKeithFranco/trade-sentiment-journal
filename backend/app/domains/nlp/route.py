from fastapi import APIRouter

from app.domains.nlp.schemas import NLPRequest, NLPResponse
from app.domains.nlp.service import NLPServiceDependency
from app.security import CurrentUserDependency

router = APIRouter(prefix="/analyze", tags=["nlp"])


@router.post("", response_model=NLPResponse)
async def analyze(
    nlp_request: NLPRequest,
    current_user: CurrentUserDependency,  # used to make sure API caller is registers user
    nlp_service: NLPServiceDependency,
) -> NLPResponse:
    return await nlp_service.inference(nlp_request.text)
