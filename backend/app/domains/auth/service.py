from typing import Annotated

from fastapi import Depends

from app.domains.auth.exceptions import (
    UserAlreadyExistsError,
    UserInvalidCredentialsError,
)
from app.domains.auth.repository import AuthRepoDependency, AuthRepository
from app.domains.auth.schemas import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.security import hash_password, run_dummy_password_verification, verify_password
from app.security.token import create_access_token, create_refresh_token


class AuthService:
    def __init__(self, auth_repo: AuthRepoDependency) -> None:
        self.auth_repo: AuthRepository = auth_repo

    async def register(self, user_register_info: UserRegisterRequest) -> UserResponse:
        existing_user = await self.auth_repo.get_user_by_email(user_register_info.email)

        if existing_user is not None:
            raise UserAlreadyExistsError(
                f"User with email {user_register_info.email} already exists"
            )

        user = await self.auth_repo.insert_user(
            email=user_register_info.email,
            hashed_password=hash_password(user_register_info.password),
        )

        await self.auth_repo.commit()

        return UserResponse.model_validate(user)

    async def login(self, user_login_info: UserLoginRequest) -> TokenResponse:
        existing_user = await self.auth_repo.get_user_by_email(user_login_info.email)

        if existing_user is None:
            # for timing
            run_dummy_password_verification()

            raise UserInvalidCredentialsError(
                f"User does not exist with email {user_login_info.email} does not exist."
            )

        if not verify_password(user_login_info.password, existing_user.hashed_password):
            raise UserInvalidCredentialsError("Password is incorrect.")

        access_token = create_access_token(existing_user.public_id)

        refresh_token_info = create_refresh_token()
        refresh_token_record = await self.auth_repo.insert_refresh_token(
            existing_user.id, *refresh_token_info
        )

        await self.auth_repo.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_record.token,
        )


AuthServiceDependency = Annotated[AuthService, Depends(AuthService)]
