import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def seed_db(client: TestClient, access_token: str) -> None:
    pass


class TestAnalytics:
    pass
