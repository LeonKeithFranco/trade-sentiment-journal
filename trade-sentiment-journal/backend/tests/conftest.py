import pytest


@pytest.fixture(scope="session")
def default_password() -> str:
    """Provide a password meeting the application's complexity requirements."""
    return "Password1!Password1!"
