import uuid

import pytest
from fastapi import status
from fastapi.testclient import TestClient


class TestCreateJournalEntry:
    @pytest.mark.parametrize(
        "payload",
        [
            {
                "title": None,
                "entry": "This is a journal message. This is a journal message.",
            },
            {
                "title": "Entry Title",
                "entry": "This is a journal entry message. This is a journal entry message.",
            },
        ],
    )
    def test_create_journal_entry(
        self,
        client: TestClient,
        access_token: str,
        payload: dict,
        trade_public_id: str,
    ) -> None:
        payload = payload | {"trade_public_id": trade_public_id}

        response = client.post(
            "/journal-entries",
            headers={"Authorization": f"Bearer {access_token}"},
            json=payload,
        )

        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()

        assert data["title"] == payload["title"]
        assert data["entry"] == payload["entry"]
        assert "public_id" in data
        assert "created_on" in data
        assert "updated_on" in data

    def test_create_journal_entry_for_nonexistent_user(
        self,
        client: TestClient,
        access_token: str,
        trade_public_id: str,
        fake_access_token: str,
    ) -> None:
        payload = {
            "title": None,
            "entry": "This is a journal message. This is a journal message.",
            "trade_public_id": trade_public_id,
        }

        response = client.post(
            "/journal-entries",
            headers={"Authorization": f"Bearer {fake_access_token}"},
            json=payload,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Token is invalid"}

    def test_create_journal_entry_on_nonexistent_trade(
        self, client: TestClient, access_token: str
    ) -> None:
        payload = {
            "title": None,
            "entry": "This is a journal message. This is a journal message.",
            "trade_public_id": str(uuid.uuid4()),
        }

        response = client.post(
            "/journal-entries",
            headers={"Authorization": f"Bearer {access_token}"},
            json=payload,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Trade(s) does not exist."}

    def test_create_journal_for_other_user(
        self,
        client: TestClient,
        access_token: str,
        other_access_token: str,
        trade_public_id: str,
    ) -> None:
        payload = {
            "title": None,
            "entry": "This is a journal message. This is a journal message.",
            "trade_public_id": trade_public_id,
        }

        response = client.post(
            "/journal-entries",
            headers={"Authorization": f"Bearer {other_access_token}"},
            json=payload,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Trade(s) does not exist."}


class TestGetJournalEntry:
    def test_get_journal_entry(
        self, client: TestClient, access_token: str, trade_public_id: str
    ) -> None:
        payload = {
            "title": None,
            "entry": "This is a journal message. This is a journal message.",
            "trade_public_id": trade_public_id,
        }

        create_response = client.post(
            "/journal-entries",
            headers={"Authorization": f"Bearer {access_token}"},
            json=payload,
        )

        get_response = client.get(
            f"/journal-entries/{create_response.json()['public_id']}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json() == create_response.json()
