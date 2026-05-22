import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

_ALLOWED_SYMBOLS = r"!@#$%^&*()_+\-="
_DISALLOWED_SYMBOLS = r"\\\'\"<>;[\]|`~"


class UserBase(BaseModel):
    email: EmailStr


class UserRegisterRequest(UserBase):
    password: str = Field(
        min_length=12,
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
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
    password: str


class UserResponse(UserBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    public_id: uuid.UUID
    created_on: datetime


class TokenBase(BaseModel):
    refresh_token: str


class TokenResponse(TokenBase):
    access_token: str
    token_type: str = "bearer"
