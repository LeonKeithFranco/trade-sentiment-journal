import random
import time
import uuid
from datetime import UTC, datetime

import pytest
from app.models import JournalEntry, SentimentAnalysis
from fastapi import status
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy import Engine, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session

random.seed(0)


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

    def test_create_journal_entry_and_sentiment(
        self,
        mocker: MockerFixture,
        db_engine: Engine,
        async_session_factory: async_sessionmaker[AsyncSession],
        client: TestClient,
        access_token: str,
        trade_public_id: str,
    ) -> None:
        mocker.patch(
            "app.domains.nlp.tasks.AsyncSessionFactory", new=async_session_factory
        )

        payload = {
            "title": "Title",
            "entry": "This is a journal message. This is a journal message.",
            "trade_public_id": trade_public_id,
        }

        response = client.post(
            "/journal-entries",
            headers={"Authorization": f"Bearer {access_token}"},
            json=payload,
        )

        with Session(db_engine) as session:
            query = (
                select(SentimentAnalysis)
                .join(JournalEntry)
                .where(
                    JournalEntry.public_id == uuid.UUID(response.json()["public_id"])
                )
            )
            results = session.execute(query)
            sentiment_analysis = results.scalar_one_or_none()

        assert sentiment_analysis is not None

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

    def test_get_non_existent_journal_entry(
        self, client: TestClient, access_token: str
    ) -> None:
        response = client.get(
            f"/journal-entries/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Journal entry or entries do not exist."

    def test_get_journal_entry_of_another_user(
        self,
        client: TestClient,
        access_token: str,
        trade_public_id: str,
        other_access_token: str,
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

        response = client.get(
            f"/journal-entries/{create_response.json()['public_id']}",
            headers={"Authorization": f"Bearer {other_access_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Journal entry or entries do not exist."

    @pytest.mark.parametrize(
        "num_entries",
        [0, 1, 3],
    )
    def test_get_all_entries(
        self,
        client: TestClient,
        access_token: str,
        trade_public_id: str,
        num_entries: int,
    ) -> None:
        payloads = [
            {
                "title": f"{random.randint(1, 1_000_000)}",
                "entry": "This is a journal message. This is a journal message.",
                "trade_public_id": trade_public_id,
            }
            for _ in range(num_entries)
        ]

        journal_entry_response_data = []

        for payload in payloads:
            create_response = client.post(
                "/journal-entries",
                headers={"Authorization": f"Bearer {access_token}"},
                json=payload,
            )
            journal_entry_response_data.append(create_response.json())

        get_all_response = client.get(
            "/journal-entries", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert get_all_response.status_code == status.HTTP_200_OK, (
            get_all_response.json()
        )

        for journal_entry_response_datum, get_all_journal_entry_response_datum in zip(
            journal_entry_response_data, get_all_response.json()
        ):
            assert journal_entry_response_datum == get_all_journal_entry_response_datum

    def test_get_all_trade_of_another_user(
        self,
        client: TestClient,
        access_token: str,
        trade_public_id: str,
        other_access_token: str,
    ) -> None:
        payload = {
            "title": "My Journal Entry",
            "entry": "This is a journal message. This is a journal message.",
            "trade_public_id": trade_public_id,
        }

        client.post(
            "/journal-entries",
            headers={"Authorization": f"Bearer {access_token}"},
            json=payload,
        )

        client.post(
            "/journal-entries",
            headers={"Authorization": f"Bearer {access_token}"},
            json=payload,
        )

        response = client.get(
            "/journal-entries",
            headers={"Authorization": f"Bearer {other_access_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []


class TestDeleteJournalEntry:
    def test_delete_journal_entry(
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

        delete_response = client.delete(
            f"/journal-entries/{create_response.json()['public_id']}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        get_response = client.get(
            f"/journal-entries/{create_response.json()['public_id']}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_non_existent_journal_entry(
        self, client: TestClient, access_token: str
    ) -> None:
        response = client.delete(
            f"/journal-entries/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Journal entry or entries do not exist."}

    def test_delete_journal_entry_of_another_user(
        self,
        client: TestClient,
        access_token: str,
        trade_public_id: str,
        other_access_token: str,
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

        trade_public_id = create_response.json()["public_id"]

        response = client.delete(
            f"/journal-entries/{trade_public_id}",
            headers={"Authorization": f"Bearer {other_access_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Journal entry or entries do not exist."}

    def test_delete_from_multiple(
        self, client: TestClient, trade_public_id: str, access_token: str
    ) -> None:
        payload = {
            "title": "Title",
            "entry": "This is a journal message. This is a journal message.",
            "trade_public_id": trade_public_id,
        }

        client.post(
            "/journal-entries",
            headers={"Authorization": f"Bearer {access_token}"},
            json=payload,
        )

        create_response = client.post(
            "/journal-entries",
            headers={"Authorization": f"Bearer {access_token}"},
            json=payload,
        )

        before_delete_get_response = client.get(
            "/journal-entries", headers={"Authorization": f"Bearer {access_token}"}
        )

        client.delete(
            f"/journal-entries/{create_response.json()['public_id']}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        after_delete_get_response = client.get(
            "/journal-entries", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert len(before_delete_get_response.json()) == 2
        assert len(after_delete_get_response.json()) == 1


class TestUpdateJournalEntry:
    def test_update_journal_entry(
        self, client: TestClient, access_token: str, trade_public_id: str
    ) -> None:
        create_payload = {
            "title": None,
            "entry": "This is a journal message. This is a journal message.",
            "trade_public_id": trade_public_id,
        }

        create_response = client.post(
            "/journal-entries",
            headers={"Authorization": f"Bearer {access_token}"},
            json=create_payload,
        )

        create_data = create_response.json()

        update_payload = {
            "title": "New Title",
        }

        update_response = client.patch(
            f"/journal-entries/{create_data['public_id']}",
            headers={"Authorization": f"Bearer {access_token}"},
            json=update_payload,
        )

        assert update_response.status_code == status.HTTP_200_OK, create_response.json()

        update_data = update_response.json()

        assert (update_data["title"] != create_data["title"]) and (
            update_data["title"] == update_payload["title"]
        )
        assert update_data["entry"] == create_data["entry"]
        assert update_data["created_on"] == create_data["created_on"]
        assert datetime.fromisoformat(
            update_data["updated_on"]
        ) > datetime.fromisoformat(create_data["updated_on"])

    def test_update_non_existent_journal_entry(
        self,
        client: TestClient,
        access_token: str,
    ) -> None:
        response = client.patch(
            f"/journal-entries/{uuid.uuid4()}",
            json={"title": "New Title"},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Journal entry or entries do not exist."}

    def test_update_journal_entry_of_another_user(
        self,
        client: TestClient,
        access_token: str,
        trade_public_id: str,
        other_access_token: str,
    ) -> None:
        create_payload = {
            "title": "Title",
            "entry": "This is a journal message. This is a journal message.",
            "trade_public_id": trade_public_id,
        }

        create_response = client.post(
            "/journal-entries",
            headers={"Authorization": f"Bearer {access_token}"},
            json=create_payload,
        )

        journal_entry_public_id = create_response.json()["public_id"]

        response = client.patch(
            f"/journal-entries/{journal_entry_public_id}",
            headers={"Authorization": f"Bearer {other_access_token}"},
            json={"title": "New Title"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Journal entry or entries do not exist."}
