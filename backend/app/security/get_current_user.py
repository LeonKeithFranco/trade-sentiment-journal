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
    """Resolve the authenticated user from a bearer access token.

    Used as a FastAPI dependency to protect routes that require
    authentication.

    Args:
        token: The bearer access token extracted from the request's
            Authorization header.
        user_repo: The UserRepository instance, provided by FastAPI's
            dependency injection.

    Returns:
        User: The authenticated user.

    Raises:
        InvalidAccessTokenError: If the token is expired, invalid, of the
            wrong type, or missing a subject.
        UserInvalidCredentialsError: If the token's subject does not match
            any existing user.
    """
    user_public_id = uuid.UUID(decode_access_token(token))
    user = await user_repo.get_user_by_public_id(user_public_id)

    if user is None:
        raise UserInvalidCredentialsError(
            f"User with public id {user_public_id} does not exist"
        )

    return user


CurrentUserDependency = Annotated[User, Depends(_get_current_user)]
