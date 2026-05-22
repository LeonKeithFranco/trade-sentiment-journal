import jwt
from app.core.config import get_settings
from app.security.token import _ALGORITHM


def jwt_encode(payload: dict) -> str:
    return jwt.encode(
        payload, key=get_settings().security.token_secret, algorithm=_ALGORITHM
    )
