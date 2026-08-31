from fastapi import APIRouter, status

from app.domains.auth.schemas import (
    RefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.domains.auth.service import AuthServiceDependency
from app.models import User
from app.security import CurrentUserDependency

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user_register_request: UserRegisterRequest, auth_service: AuthServiceDependency
) -> UserResponse:
    """Register a new user account.

    Args:
        user_register_request: The request body containing the new user's
            email and password.
        auth_service: The injected AuthService instance.

    Returns:
        UserResponse: The newly created user.

    Raises:
        UserAlreadyExistsError: If a user with the given email already exists.
    """
    return await auth_service.register(user_register_request)


@router.post("/login", response_model=TokenResponse)
async def login(
    user_login_request: UserLoginRequest, auth_service: AuthServiceDependency
) -> TokenResponse:
    """Authenticate a user and issue a new access and refresh token pair.

    Args:
        user_login_request: The request body containing the user's email and
            password.
        auth_service: The injected AuthService instance.

    Returns:
        TokenResponse: The newly issued access and refresh tokens.

    Raises:
        UserInvalidCredentialsError: If the email does not match a registered
            user or the password is incorrect.
    """
    return await auth_service.login(user_login_request)


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUserDependency) -> User:
    """Return the currently authenticated user.

    Args:
        current_user: The authenticated user making the request.

    Returns:
        User: The currently authenticated user.
    """
    return current_user


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    refresh_request: RefreshRequest, auth_service: AuthServiceDependency
) -> TokenResponse:
    """Exchange a valid refresh token for a new access and refresh token pair.

    The provided refresh token is revoked once the new pair is issued.

    Args:
        refresh_request: The request body containing the refresh token.
        auth_service: The injected AuthService instance.

    Returns:
        TokenResponse: The newly issued access and refresh tokens.

    Raises:
        UserInvalidCredentialsError: If the refresh token is invalid, revoked,
            or expired.
    """
    return await auth_service.refresh_tokens(refresh_request)
