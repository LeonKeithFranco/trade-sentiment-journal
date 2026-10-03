import pytest
from app.domains.nlp.constants import SentimentEnum
from fastapi import status
from fastapi.testclient import TestClient


class TestAnalyze:
    """Integration tests for the POST /analyze endpoint."""

    @pytest.mark.parametrize(
        "text",
        (
            "This is some text",
            "Profit up revenue up",
            "Crash loss bankruptcy",
        ),
    )
    def test_analyze(self, client: TestClient, access_token: str, text: str) -> None:
        """Verify analyzing text returns a valid sentiment and confidence score."""
        response = client.post(
            "/analyze",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"text": text},
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        SentimentEnum(data["sentiment"])
        assert 0.0 < data["confidence"] < 1.0

    def test_analyze_empty_text(self, client: TestClient, access_token: str) -> None:
        """Verify analyzing empty text returns 422 Unprocessable Content."""
        response = client.post(
            "/analyze",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"text": ""},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        assert response.json()["detail"] == "Cannot make predictions on empty text."

    def test_not_registered_user_analyze(
        self,
        client: TestClient,
    ) -> None:
        """Verify analyzing text without authentication returns 401 Unauthorized."""
        response = client.post(
            "/analyze",
            json={"text": "Text"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        assert response.json()["detail"] == "Not authenticated"
