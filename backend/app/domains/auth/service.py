from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends

from app.domains.auth.exceptions import (
    UserAlreadyExistsError,
    UserInvalidCredentialsError,
)
from app.domains.auth.repository import (
    RefreshTokenRepoDependency,
    RefreshTokenRepository,
    UserRepoDependency,
    UserRepository,
)
from app.domains.auth.schemas import (
    RefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.models import User
from app.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    run_dummy_password_verification,
    verify_password,
)


class AuthService:
    def __init__(
        self,
        user_repo: UserRepoDependency,
        refresh_token_repo: RefreshTokenRepoDependency,
    ) -> None:
        self.user_repo: UserRepository = user_repo
        self.refresh_token_repo: RefreshTokenRepository = refresh_token_repo

    async def _create_new_tokens(self, user: User) -> tuple[str, str]:
        access_token = create_access_token(user.public_id)

        refresh_token_info = create_refresh_token()
        refresh_token_record = await self.refresh_token_repo.insert_refresh_token(
            user.id, *refresh_token_info
        )

        return access_token, refresh_token_record.token

    async def register(self, user_register_info: UserRegisterRequest) -> UserResponse:
        existing_user = await self.user_repo.get_user_by_email(user_register_info.email)

        if existing_user is not None:
            raise UserAlreadyExistsError(
                f"User with email {user_register_info.email} already exists"
            )

        user = await self.user_repo.insert_user(
            email=user_register_info.email,
            hashed_password=hash_password(user_register_info.password),
        )

        await self.user_repo.commit()

        return UserResponse.model_validate(user)

    async def login(self, user_login_info: UserLoginRequest) -> TokenResponse:
        existing_user = await self.user_repo.get_user_by_email(user_login_info.email)

        if existing_user is None:
            # for timing
            run_dummy_password_verification()

            raise UserInvalidCredentialsError(
                f"User with email {user_login_info.email} does not exist."
            )

        if not verify_password(user_login_info.password, existing_user.hashed_password):
            raise UserInvalidCredentialsError("Password is incorrect.")

        access_token, refresh_token = await self._create_new_tokens(existing_user)

        await self.refresh_token_repo.commit()

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def refresh_tokens(self, refresh_info: RefreshRequest) -> TokenResponse:
        refresh_token_record = await self.refresh_token_repo.get_refresh_token(
            refresh_info.refresh_token
        )

        if refresh_token_record is None:
            raise UserInvalidCredentialsError("Invalid refresh token")

        if refresh_token_record.expires_on < datetime.now(UTC):
            raise UserInvalidCredentialsError("Refresh token is expired")

        access_token, refresh_token = await self._create_new_tokens(
            refresh_token_record.user
        )

        await self.refresh_token_repo.commit()

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)


AuthServiceDependency = Annotated[AuthService, Depends(AuthService)]
