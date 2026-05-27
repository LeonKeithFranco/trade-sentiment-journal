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
        trade_public_id:str,
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
