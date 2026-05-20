from fastapi import APIRouter

from app.domains.auth.schemas import UserRegisterRequest, UserResponse
from app.domains.auth.service import AuthServiceDependency

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/register", response_model=UserResponse)
async def register(
    user_register_request: UserRegisterRequest, auth_service: AuthServiceDependency
) -> UserResponse:
    return await auth_service.register(user_register_request)
