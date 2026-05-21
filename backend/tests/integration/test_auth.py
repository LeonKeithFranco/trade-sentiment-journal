import pytest
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response


@pytest.fixture
def registered_user_response(client: TestClient, default_password: str) -> Response:
    response = client.post(
        "/auth/register", json={"email": "user@test.com", "password": default_password}
    )

    return response


class TestRegister:
    def test_register_user(self, registered_user_response: Response) -> None:
        assert registered_user_response.status_code == status.HTTP_201_CREATED

        data = registered_user_response.json()

        assert "password" not in data
        assert "hashed_password" not in data
        assert "public_id" in data
        assert data["email"] == "user@test.com"

    def test_duplicate_email(
        self,
        client: TestClient,
        registered_user_response: Response,  # included to make sure first user is registered
        default_password: str,
    ) -> None:
        response = client.post(
            "/auth/register",
            json={"email": "user@test.com", "password": default_password},
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json() == {"detail": "User already exists."}

    def test_short_password(self, client: TestClient) -> None:
        # under character min but otherwise valid
        short_password = "Password1!"

        response = client.post(
            "/auth/register",
            json={"email": "user@test.com", "password": short_password},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json()["detail"][0] == {
            "type": "string_too_short",
            "loc": ["body", "password"],
            "msg": "String should have at least 12 characters",
            "input": "Password1!",
            "ctx": {"min_length": 12},
        }

    @pytest.mark.parametrize(
        "invalid_password,message",
        [
            (
                "password1!password1!",
                "Value error, Password must contain at least one uppercase letter",
            ),
            (
                "PASSWORD1!PASSWORD1!",
                "Value error, Password must contain at least one lowercase letter",
            ),
            (
                "Password!Password!",
                "Value error, Password must contain at least one number",
            ),
            (
                "Password1Password1",
                "Value error, Password must contain at least one of: !@#$%^&*()_+\\-=",
            ),
            (
                "Password1!\\Password1!\\",
                "Value error, Password can't contain any of: \\\\\\'\\\"<>;[\\]|`~",
            ),
        ],
    )
    def test_invalid_password(
        self, invalid_password: str, message: str, client: TestClient
    ) -> None:
        response = client.post(
            "/auth/register",
            json={"email": "user@test.com", "password": invalid_password},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json()["detail"][0] == {
            "type": "value_error",
            "loc": ["body", "password"],
            "msg": message,
            "input": invalid_password,
            "ctx": {"error": {}},
        }
