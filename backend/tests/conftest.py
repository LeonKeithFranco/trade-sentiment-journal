import pytest


@pytest.fixture(scope="session")
def default_password() -> str:
    return "Password1!Password1!"
