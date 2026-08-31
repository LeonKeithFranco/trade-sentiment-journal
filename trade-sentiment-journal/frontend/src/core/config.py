from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class _AppSettings(BaseModel):
    """General frontend application settings.

    Attributes:
        name: The display name of the application.
        debug: Whether to enable debug mode.
    """

    name: str = "App Name"
    debug: bool = True


class _APISettings(BaseModel):
    """Settings for connecting to the backend API.

    Attributes:
        base_url: The base URL of the backend API.
        time_out: The request timeout in seconds.
    """

    base_url: str
    time_out: float = 30.0


class _Settings(BaseSettings):
    """Frontend application settings loaded from environment variables or .env.

    Attributes:
        app: General application settings.
        api: Backend API connection settings.
    """

    model_config = SettingsConfigDict(
        env_file=[
            Path(__file__).parent.parent.parent.parent / ".env",
            Path(__file__).parent.parent.parent / ".env",
        ],
        env_nested_delimiter="__",
        env_ignore_empty=True,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app: _AppSettings = Field(default_factory=_AppSettings)
    api: _APISettings = Field(default_factory=_APISettings)


@lru_cache
def get_settings() -> _Settings:
    """Return the cached application settings singleton.

    Returns:
        _Settings: The frontend settings instance.
    """
    return _Settings()
