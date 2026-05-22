import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.domains.auth.repository import UserRepoDependency
from app.exceptions import UserInvalidCredentialsError
from app.models import User
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def _get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], user_repo: UserRepoDependency
) -> User:
    user_public_id = uuid.UUID(decode_access_token(token))
    user = await user_repo.get_user_by_public_id(user_public_id)

    if user is None:
        raise UserInvalidCredentialsError(
            f"User with public id {user_public_id} does not exist"
        )

    return user


CurrentUserDependency = Annotated[User, Depends(_get_current_user)]
