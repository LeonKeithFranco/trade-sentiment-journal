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
    """Service layer for user registration, login, and token management.

    Attributes:
        user_repo: The repository used for user database access.
        refresh_token_repo: The repository used for refresh token database
            access.
    """

    def __init__(
        self,
        user_repo: UserRepoDependency,
        refresh_token_repo: RefreshTokenRepoDependency,
    ) -> None:
        """Initialize the service with injected user and refresh token repositories.

        Args:
            user_repo: The UserRepository instance, provided by FastAPI's
                dependency injection.
            refresh_token_repo: The RefreshTokenRepository instance, provided
                by FastAPI's dependency injection.
        """
        self.user_repo: UserRepository = user_repo
        self.refresh_token_repo: RefreshTokenRepository = refresh_token_repo

    async def _create_new_tokens(self, user: User) -> tuple[str, str]:
        """Issue a new access and refresh token pair for a user.

        Persists the new refresh token to the database, but does not commit
        the transaction; the caller is responsible for committing.

        Args:
            user: The user to issue tokens for.

        Returns:
            tuple: A tuple of (access_token, refresh_token) strings.
        """
        access_token = create_access_token(user.public_id)

        refresh_token_info = create_refresh_token()
        refresh_token_record = await self.refresh_token_repo.insert_refresh_token(
            user.id, *refresh_token_info
        )

        return access_token, refresh_token_record.token

    async def register(self, user_register_info: UserRegisterRequest) -> UserResponse:
        """Register a new user account.

        Hashes and peppers the plaintext password before storing it.

        Args:
            user_register_info: The new user's email and plaintext password.

        Returns:
            UserResponse: The newly created user.

        Raises:
            UserAlreadyExistsError: If a user with the given email already
                exists.
        """
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
        """Authenticate a user and issue a new access and refresh token pair.

        Runs a dummy password verification when the email is not found so
        that login attempts for non-existent and existing users take a
        similar amount of time.

        Args:
            user_login_info: The user's email and plaintext password.

        Returns:
            TokenResponse: The newly issued access and refresh tokens.

        Raises:
            UserInvalidCredentialsError: If the email does not match a
                registered user or the password is incorrect.
        """
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
        """Exchange a valid refresh token for a new access and refresh token pair.

        Validates that the refresh token exists, has not been revoked, and
        has not expired, then issues a new token pair and revokes the
        provided refresh token.

        Args:
            refresh_info: The refresh token to exchange.

        Returns:
            TokenResponse: The newly issued access and refresh tokens.

        Raises:
            UserInvalidCredentialsError: If the refresh token is invalid,
                revoked, or expired.
        """
        refresh_token_record = await self.refresh_token_repo.get_refresh_token(
            refresh_info.refresh_token
        )

        if refresh_token_record is None:
            raise UserInvalidCredentialsError("Invalid refresh token")

        if refresh_token_record.revoked:
            raise UserInvalidCredentialsError("Refresh token is revoked")

        if refresh_token_record.expires_on < datetime.now(UTC):
            raise UserInvalidCredentialsError("Refresh token is expired")

        access_token, refresh_token = await self._create_new_tokens(
            refresh_token_record.user
        )

        await self.refresh_token_repo.revoke_refresh_token(refresh_info.refresh_token)

        await self.refresh_token_repo.commit()

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)


AuthServiceDependency = Annotated[AuthService, Depends(AuthService)]
