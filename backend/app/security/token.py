import uuid
from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import get_settings
from app.security.exceptions import InvalidAccessTokenError

_security_settings = get_settings().security

_ALGORITHM = "HS256"


def create_access_token(user_public_id: uuid.UUID) -> str:
    current_time = datetime.now(UTC)
    expire_time = current_time + timedelta(
        minutes=_security_settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_public_id),
        "type": "access",
        "exp": expire_time,
        "iat": current_time,
    }

    return jwt.encode(
        payload, key=_security_settings.token_secret, algorithm=_ALGORITHM
    )


def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token, key=_security_settings.token_secret, algorithm=_ALGORITHM
        )
    except jwt.ExpiredSignatureError as exc:
        raise InvalidAccessTokenError("Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise InvalidAccessTokenError("Token is invalid") from exc

    if payload.get("type") != "access":
        raise InvalidAccessTokenError("Token type is incorrect")

    if not payload.get("sub"):
        raise InvalidAccessTokenError("Token subject is missing")

    return payload["sub"]
