from typing import Annotated

from fastapi import Depends

from app.auth.exceptions import UserAlreadyExists
from app.auth.models import User
from app.auth.repository import AuthRepoDependency
from app.auth.schemas import UserRegisterRequest, UserResponse
from app.security import hash_password


class AuthService:
    async def register(
        self, auth_repo: AuthRepoDependency, user_register_info: UserRegisterRequest
    ) -> UserResponse:
        existing_user = await auth_repo.get_user_by_email(user_register_info.email)

        if existing_user is None:
            raise UserAlreadyExists(
                f"User with email {user_register_info.email} already exists"
            )

        user = await auth_repo.insert_user(
            email=user_register_info.email,
            hashed_password=hash_password(user_register_info.password),
        )

        await auth_repo.commit()

        return UserResponse.model_validate(user)


AuthServiceDependency = Annotated[AuthService, Depends(AuthService)]
