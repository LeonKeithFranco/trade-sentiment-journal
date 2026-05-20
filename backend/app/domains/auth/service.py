from typing import Annotated

from fastapi import Depends

from app.domains.auth.repository import AuthRepoDependency, AuthRepository
from app.domains.auth.schemas import UserRegisterRequest, UserResponse
from app.exceptions import UserAlreadyExistsError
from app.security import hash_password


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


AuthServiceDependency = Annotated[AuthService, Depends(AuthService)]
