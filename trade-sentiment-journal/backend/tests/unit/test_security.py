import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from app.core.config import get_settings
from app.exceptions import InvalidAccessTokenError
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.security.password import _pepper_password
from app.security.token import _ALGORITHM
from pwdlib.exceptions import UnknownHashError
from pytest_mock import MockerFixture
from tests.utils import jwt_encode


@pytest.fixture(scope="session")
def hashed_password(default_password: str) -> str:
    """Provide the peppered and hashed form of the default test password."""
    return hash_password(default_password)


@pytest.fixture(scope="session")
def fake_user_public_id() -> uuid.UUID:
    """Provide a fixed UUID to use as a fake user's public ID."""
    return uuid.UUID("d5c7c282-b35a-4a7c-b361-c3aa7b4b1715")


class TestPassword:
    """Unit tests for password hashing and verification."""

    def test_hashing(self, hashed_password: str) -> None:
        """Verify a hashed password has the expected argon2id format and parameters."""
        argon2_hashed_password_components = hashed_password.split("$")

        algo_type = argon2_hashed_password_components[1]
        assert algo_type == "argon2id"

        version = argon2_hashed_password_components[2]
        assert "v=" in version

        configuration = argon2_hashed_password_components[3]
        assert configuration == "m=65536,t=3,p=4"

        salt = argon2_hashed_password_components[4]
        assert 22 <= len(salt) <= 24

        hash = argon2_hashed_password_components[5]
        assert 43 <= len(hash) <= 44

    def test_verification(self, default_password: str, hashed_password: str) -> None:
        """Verify a correct password matches its hash and an incorrect one does not."""
        assert verify_password(default_password, hashed_password)
        assert not verify_password("not" + default_password, hashed_password)

    def test_verification_when_exception_thrown(
        self, mocker: MockerFixture, default_password: str, hashed_password: str
    ) -> None:
        """Verify verify_password returns False rather than raising on an unrecognized hash."""
        mock_verify = mocker.patch(
            "app.security.password._hasher.verify",
            side_effect=UnknownHashError(""),
        )

        assert not verify_password(default_password, hashed_password)

        mock_verify.assert_called_once_with(
            password=_pepper_password(default_password), hash=hashed_password
        )


class TestAccessToken:
    """Unit tests for access token creation and decoding."""

    def test_create_and_decode_access_token(
        self, fake_user_public_id: uuid.UUID
    ) -> None:
        """Verify a created access token decodes back to the original user's public ID."""
        access_token = create_access_token(fake_user_public_id)
        decoded_user_id = decode_access_token(access_token)

        assert decoded_user_id == str(fake_user_public_id)

    def test_decode_expired_access_token(self, fake_user_public_id: uuid.UUID) -> None:
        """Verify decoding an expired access token raises InvalidAccessTokenError."""
        expired_payload = {
            "sub": str(fake_user_public_id),
            "type": "access",
            "exp": datetime.now(UTC)
            - timedelta(minutes=get_settings().security.access_token_expire_minutes),
        }

        token = jwt_encode(expired_payload)

        with pytest.raises(InvalidAccessTokenError, match="Token has expired"):
            decode_access_token(token)

    def test_decode_wrong_type_access_token(
        self, fake_user_public_id: uuid.UUID
    ) -> None:
        """Verify decoding a token with a non-access type raises InvalidAccessTokenError."""
        wrong_type_payload = {
            "sub": str(fake_user_public_id),
            "type": "not_access",
            "exp": datetime.now(UTC) + timedelta(minutes=5),
        }

        token = jwt_encode(wrong_type_payload)

        with pytest.raises(InvalidAccessTokenError, match="Token type is incorrect"):
            decode_access_token(token)

    def test_decode_missing_sub_access_token(self) -> None:
        """Verify decoding a token with no subject raises InvalidAccessTokenError."""
        wrong_type_payload = {
            "type": "access",
            "exp": datetime.now(UTC) + timedelta(minutes=5),
        }

        token = jwt_encode(wrong_type_payload)

        with pytest.raises(InvalidAccessTokenError, match="Token subject is missing"):
            decode_access_token(token)

    def test_decode_invalid_access_token(
        self, mocker: MockerFixture, fake_user_public_id: uuid.UUID
    ) -> None:
        """Verify a token that jwt.decode rejects as invalid raises InvalidAccessTokenError."""
        payload = {
            "sub": str(fake_user_public_id),
            "type": "access",
            "exp": datetime.now(UTC)
            + timedelta(minutes=get_settings().security.access_token_expire_minutes),
            "iat": datetime.now(UTC),
        }

        token = jwt_encode(payload)

        mock_decode = mocker.patch(
            "app.security.token.jwt.decode", side_effect=jwt.InvalidTokenError
        )

        with pytest.raises(InvalidAccessTokenError, match="Token is invalid"):
            decode_access_token(token)

        mock_decode.assert_called_once_with(
            token, key=get_settings().security.token_secret, algorithms=[_ALGORITHM]
        )


class TestRefreshToken:
    """Unit tests for refresh token creation."""

    def test_create_refresh_token(self) -> None:
        """Verify a created refresh token expires after the configured number of days."""
        token, expire = create_refresh_token()
        today = datetime.now(UTC)
        diff_days = (expire.date() - today.date()).days

        assert diff_days == get_settings().security.refresh_token_expire_days
