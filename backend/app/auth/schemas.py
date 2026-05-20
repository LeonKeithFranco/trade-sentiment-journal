import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr


class UserRequest(UserBase):
    password: str = Field(
        min_length=12,
    )


class UserResponse(UserBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    public_id: uuid.UUID
    created_on: datetime
