import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

_ALLOWED_SYMBOLS = r"!@#$%^&*()_+\-="
_DISALLOWED_SYMBOLS = r"\\\'\"<>;[\]|`~"


class UserBase(BaseModel):
    """Base schema for user-related requests and responses.

    Attributes:
        email: The user's email address.
    """

    email: EmailStr


class UserRegisterRequest(UserBase):
    """Pydantic request model for the POST /auth/register endpoint.

    Attributes:
        password: The user's plaintext password. Must be at least 12
            characters and meet the complexity rules enforced by
            validate_password.
    """

    password: str = Field(
        min_length=12,
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate that a password meets the application's complexity requirements.

        Requires at least one uppercase letter, one lowercase letter, one
        number, and one allowed symbol, and rejects any disallowed symbols.

        Args:
            v: The plaintext password to validate.

        Returns:
            str: The validated password, unchanged.

        Raises:
            ValueError: If the password is missing a required character type
                or contains a disallowed symbol.
        """
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(rf"[{_ALLOWED_SYMBOLS}]", v):
            raise ValueError(
                f"Password must contain at least one of: {_ALLOWED_SYMBOLS}"
            )
        if re.search(rf"[{_DISALLOWED_SYMBOLS}]", v):
            raise ValueError(f"Password can't contain any of: {_DISALLOWED_SYMBOLS}")

        return v


class UserLoginRequest(UserBase):
    """Pydantic request model for the POST /auth/login endpoint.

    Attributes:
        password: The user's plaintext password.
    """

    password: str


class UserResponse(UserBase):
    """Pydantic response model for user-related endpoints.

    Attributes:
        public_id: The user's public-facing UUID.
        created_on: The UTC timestamp when the user account was created.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    public_id: uuid.UUID
    created_on: datetime


class TokenBase(BaseModel):
    """Base schema for token-related requests and responses.

    Attributes:
        refresh_token: The refresh token string.
    """

    refresh_token: str


class TokenResponse(TokenBase):
    """Pydantic response model for the POST /auth/login and POST /auth/refresh endpoints.

    Attributes:
        access_token: The short-lived JWT access token.
        token_type: The token type, always "bearer".
    """

    access_token: str
    token_type: str = "bearer"


class RefreshRequest(TokenBase):
    """Pydantic request model for the POST /auth/refresh endpoint."""

    pass
