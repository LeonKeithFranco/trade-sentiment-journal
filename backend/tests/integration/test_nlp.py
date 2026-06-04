import pytest
from fastapi import status
from fastapi.testclient import TestClient


class TestAnalyze:
    @pytest.mark.parametrize(
        "text,sentiment",
        (
            ("This is some text", "neutral"),
            ("Profit up revenue up", "positive"),
            ("Crash loss bankruptcy", "negative"),
        ),
    )
    def test_analyze(
        self, client: TestClient, access_token: str, text: str, sentiment: str
    ) -> None:
        response = client.post(
            "/analyze",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"text": text},
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data["sentiment"] == sentiment
        assert 0.5 < data["confidence"] < 1.0

    def test_analyze_empty_text(self, client: TestClient, access_token: str) -> None:
        response = client.post(
            "/analyze",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"text": ""},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

        assert response.json()["detail"] == "Cannot make predictions on empty text."
