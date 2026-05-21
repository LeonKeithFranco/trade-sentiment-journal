from fastapi import APIRouter, status

from app.domains.auth.schemas import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.domains.auth.service import AuthServiceDependency

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user_register_request: UserRegisterRequest, auth_service: AuthServiceDependency
) -> UserResponse:
    return await auth_service.register(user_register_request)


@router.post("/login", response_model=TokenResponse)
async def login(
    user_login_request: UserLoginRequest, auth_service: AuthServiceDependency
) -> TokenResponse:
    return await auth_service.login(user_login_request)
