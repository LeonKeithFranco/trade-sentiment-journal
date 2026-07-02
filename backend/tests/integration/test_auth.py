import secrets
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import Engine, text
from tests.utils import jwt_encode


@pytest.fixture
def registered_user_response(client: TestClient, default_password: str) -> Response:
    """Register a default test user and return the raw registration response.

    Args:
        client: The test client to make requests with.
        default_password: The password to register with.

    Returns:
        Response: The raw HTTP response from the registration request.
    """
    response = client.post(
        "/auth/register", json={"email": "user@test.com", "password": default_password}
    )

    return response


class TestRegister:
    """Integration tests for the POST /auth/register endpoint."""

    def test_register_user(self, registered_user_response: Response) -> None:
        """Verify registering a new user returns the created user without sensitive fields."""
        assert registered_user_response.status_code == status.HTTP_201_CREATED

        data = registered_user_response.json()

        assert "password" not in data
        assert "hashed_password" not in data
        assert "public_id" in data
        assert data["email"] == "user@test.com"
        assert datetime.fromisoformat(data["created_on"]) <= datetime.now(UTC)

    def test_duplicate_email(
        self,
        client: TestClient,
        registered_user_response: Response,  # included to make sure first user is registered
        default_password: str,
    ) -> None:
        """Verify registering with an already-used email returns 409 Conflict."""
        response = client.post(
            "/auth/register",
            json={"email": "user@test.com", "password": default_password},
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json() == {"detail": "User already exists."}

    def test_short_password(self, client: TestClient) -> None:
        """Verify a password under the minimum length returns 422 Unprocessable Content."""
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
        """Verify each password complexity rule is enforced with the expected error message."""
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


class TestLogin:
    """Integration tests for the POST /auth/login endpoint."""

    def test_login(
        self,
        client: TestClient,
        registered_user_response: Response,
        default_password: str,
    ) -> None:
        """Verify logging in with correct credentials returns a valid token pair."""
        response = client.post(
            "/auth/login",
            json={
                "email": registered_user_response.json()["email"],
                "password": default_password,
            },
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_invalid_email_login(
        self,
        client: TestClient,
        registered_user_response: Response,  # included to make sure first user is registered
    ) -> None:
        """Verify logging in with an unregistered email returns 401 Unauthorized."""
        response = client.post(
            "/auth/login",
            json={
                "email": "invalid@email.com",
                "password": "Password1!Password1!",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Invalid credentials."}

    def test_invalid_password_login(
        self,
        client: TestClient,
        registered_user_response: Response,
        default_password: str,
    ) -> None:
        """Verify logging in with an incorrect password returns 401 Unauthorized."""
        response = client.post(
            "/auth/login",
            json={
                "email": registered_user_response.json()["email"],
                "password": default_password + "!",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Invalid credentials."}


class TestMe:
    """Integration tests for the GET /auth/me endpoint."""

    def test_get_current_user(
        self,
        client: TestClient,
        registered_user_response: Response,
        default_password: str,
    ) -> None:
        """Verify a valid access token returns the matching authenticated user."""
        login_response = client.post(
            "/auth/login",
            json={
                "email": registered_user_response.json()["email"],
                "password": default_password,
            },
        )

        access_token = login_response.json()["access_token"]

        response = client.get(
            "/auth/me", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data["email"] == registered_user_response.json()["email"]
        assert data["public_id"] == registered_user_response.json()["public_id"]
        assert data["created_on"] == registered_user_response.json()["created_on"]

    def test_no_token(self, client: TestClient) -> None:
        """Verify a request with no access token returns 401 Unauthorized."""
        response = client.get("/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}

    def test_expired_token(self, client: TestClient) -> None:
        """Verify an expired access token returns 401 Unauthorized."""
        expired_payload = {
            "sub": str(uuid.uuid4()),
            "type": "access",
            "exp": datetime.now(UTC) - timedelta(minutes=1),
        }

        expired_access_token = jwt_encode(expired_payload)

        response = client.get(
            "/auth/me", headers={"Authorization": f"Bearer {expired_access_token}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Token has expired"}

    def test_invalid_token(self, client: TestClient) -> None:
        """Verify a malformed access token returns 401 Unauthorized."""
        response = client.get(
            "/auth/me", headers={"Authorization": "Bearer not.real.token"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Token is invalid"}

    def test_not_real_user(self, client: TestClient) -> None:
        """Verify a well-formed token for a non-existent user returns 401 Unauthorized."""
        payload = {
            "sub": str(uuid.uuid4()),
            "type": "access",
            "exp": datetime.now(UTC) + timedelta(minutes=10),
        }

        access_token = jwt_encode(payload)

        response = client.get(
            "/auth/me", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Invalid credentials."}


class TestRefresh:
    """Integration tests for the POST /auth/refresh endpoint."""

    def test_refresh(
        self,
        client: TestClient,
        registered_user_response: Response,
        default_password: str,
    ) -> None:
        """Verify a valid refresh token returns a new token pair with a rotated refresh token."""
        login_response = client.post(
            "/auth/login",
            json={
                "email": registered_user_response.json()["email"],
                "password": default_password,
            },
        )

        refresh_token = login_response.json()["refresh_token"]

        response = client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data["refresh_token"] != refresh_token
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_not_real_refresh_token(self, client: TestClient) -> None:
        """Verify an unrecognized refresh token returns 401 Unauthorized."""
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": secrets.token_urlsafe(64)},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Invalid credentials."}

    def test_expired_refresh_token(
        self,
        client: TestClient,
        registered_user_response: Response,
        default_password: str,
        db_engine: Engine,
    ) -> None:
        """Verify an expired refresh token returns 401 Unauthorized."""
        login_response = client.post(
            "/auth/login",
            json={
                "email": registered_user_response.json()["email"],
                "password": default_password,
            },
        )

        refresh_token = login_response.json()["refresh_token"]

        expiration = datetime.now(UTC) - timedelta(minutes=1)

        with db_engine.begin() as conn:
            conn.execute(
                text(
                    "UPDATE refresh_tokens SET expires_on = :expiration WHERE token = :refresh_token"
                ),
                {"expiration": expiration, "refresh_token": refresh_token},
            )

        response = client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Invalid credentials."}

    def test_revoked_refresh_token(
        self,
        client: TestClient,
        registered_user_response: Response,
        default_password: str,
    ) -> None:
        """Verify a refresh token that has already been used once cannot be reused."""
        login_response = client.post(
            "/auth/login",
            json={
                "email": registered_user_response.json()["email"],
                "password": default_password,
            },
        )

        old_refresh_token = login_response.json()["refresh_token"]

        client.post(
            "/auth/refresh",
            json={"refresh_token": old_refresh_token},
        )

        response = client.post(
            "/auth/refresh",
            json={"refresh_token": old_refresh_token},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Invalid credentials."}
