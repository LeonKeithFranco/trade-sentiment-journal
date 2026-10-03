from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from app.core.config import get_settings

_hasher = PasswordHash.recommended()
_security_settings = get_settings().security

DUMMY_PASSWORD = "$argon2id$v=19$m=65536,t=3,p=4$MmZ5sZQf6pExLYGXF09nTQ$rWk2xBynjf5wQYbiPAantr9Meo4l7ns+Zc9Tp5Wa5Vo"


def _pepper_password(password: str) -> str:
    """Append the application's secret pepper to a plaintext password.

    Args:
        password: The plaintext password to pepper.

    Returns:
        str: The peppered password.
    """
    return password + _security_settings.pepper_secret


def hash_password(password: str) -> str:
    """Pepper and hash a plaintext password for storage.

    Args:
        password: The plaintext password to hash.

    Returns:
        str: The peppered and hashed password.
    """
    peppered_password = _pepper_password(password)

    return _hasher.hash(peppered_password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored peppered hash.

    Args:
        password: The plaintext password to verify.
        hashed_password: The stored peppered and hashed password to check
            against.

    Returns:
        bool: True if the password matches the hash, False otherwise
            (including if the hash is in an unrecognized format).
    """
    peppered_password = _pepper_password(password)

    try:
        return _hasher.verify(
            password=peppered_password,
            hash=hashed_password,
        )
    except UnknownHashError:
        return False


def run_dummy_password_verification() -> None:
    """Run a password verification against a fixed dummy hash.

    Used to make failed logins for non-existent users take a similar amount
    of time as failed logins for existing users with an incorrect password,
    preventing user enumeration via timing.
    """
    verify_password("", DUMMY_PASSWORD)
