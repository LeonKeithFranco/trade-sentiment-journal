import secrets
import uuid
from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import get_settings
from app.security.exceptions import InvalidAccessTokenError

_security_settings = get_settings().security

_ALGORITHM = "HS256"


def create_access_token(user_public_id: uuid.UUID) -> str:
    """Create a signed JWT access token for a user.

    Args:
        user_public_id: The public UUID of the user to issue the token for.

    Returns:
        str: The encoded JWT access token, valid for the configured access
            token expiry period.
    """
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
    """Decode and validate a JWT access token, returning its subject.

    Args:
        token: The encoded JWT access token to decode.

    Returns:
        str: The token's subject, the public UUID of the user it was issued
            to, as a string.

    Raises:
        InvalidAccessTokenError: If the token is expired, cannot be decoded,
            is not an access token, or is missing a subject.
    """
    try:
        payload = jwt.decode(
            token, key=_security_settings.token_secret, algorithms=[_ALGORITHM]
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


def create_refresh_token() -> tuple[str, datetime]:
    """Create a new random refresh token and its expiry timestamp.

    Returns:
        tuple: A tuple of (token, expire), where token is a URL-safe random
            string and expire is the timestamp after which the token is no
            longer valid.
    """
    token = secrets.token_urlsafe(64)
    expire = datetime.now(UTC) + timedelta(
        days=_security_settings.refresh_token_expire_days
    )

    return token, expire
