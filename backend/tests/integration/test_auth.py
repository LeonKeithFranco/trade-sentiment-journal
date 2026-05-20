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


class TestAuth:
    def test_register_user(self, registered_user_response: Response) -> None:
        assert registered_user_response.status_code == status.HTTP_201_CREATED

        data = registered_user_response.json()

        assert "password" not in data
        assert "hashed_password" not in data
        assert "public_id" in data
        assert data["email"] == "user@test.com"
