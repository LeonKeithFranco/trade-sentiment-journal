import jwt
from app.core.config import get_settings
from app.security.token import _ALGORITHM


def jwt_encode(payload: dict) -> str:
    """Encode an arbitrary payload as a JWT using the application's signing key.

    Used in tests to construct tokens with specific claims (e.g. expired,
    malformed, or missing fields) that the application's own token-creation
    helpers would not produce.

    Args:
        payload: The claims to encode into the token.

    Returns:
        str: The encoded JWT.
    """
    return jwt.encode(
        payload, key=get_settings().security.token_secret, algorithm=_ALGORITHM
    )
