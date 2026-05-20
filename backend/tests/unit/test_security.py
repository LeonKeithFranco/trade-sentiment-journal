import pytest
from app.security import hash_password, verify_password
from app.security.password import _pepper_password
from pwdlib.exceptions import UnknownHashError
from pytest_mock import MockerFixture


@pytest.fixture(scope="session")
def hashed_password(default_password: str) -> str:
    return hash_password(default_password)


class TestSecurity:
    def test_hashing(self, hashed_password: str) -> None:
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
        assert verify_password(default_password, hashed_password)
        assert not verify_password("not" + default_password, hashed_password)

    def test_verification_when_exception_thrown(
        self, mocker: MockerFixture, default_password: str, hashed_password: str
    ) -> None:
        mock_verify = mocker.patch(
            "app.security.password._hasher.verify",
            side_effect=UnknownHashError(""),
        )

        assert not verify_password(default_password, hashed_password)

        mock_verify.assert_called_once_with(
            password=_pepper_password(default_password), hash=hashed_password
        )
