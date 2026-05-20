from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from app.core.config import get_settings

_hasher = PasswordHash.recommended()
_security_settings = get_settings().security


def _pepper_password(password: str) -> str:
    return password + _security_settings.pepper_secret


def hash_password(password: str) -> str:
    peppered_password = _pepper_password(password)

    return _hasher.hash(peppered_password)


def verify_password(password: str, hashed_password: str) -> bool:
    peppered_password = _pepper_password(password)

    try:
        return _hasher.verify(
            password=peppered_password,
            hash=hashed_password,
        )
    except UnknownHashError:
        return False
