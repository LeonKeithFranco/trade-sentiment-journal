from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class _DbSettings(BaseModel):
    host: str = "localhost"
    user: str
    password: str
    name: str
    port: int = 5432


class _AppSettings(BaseModel):
    name: str = "App Name"
    debut: bool = True


class _Settings(BaseSettings):
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

    db: _DbSettings = Field(default_factory=_DbSettings)
    app: _AppSettings = Field(default_factory=_AppSettings)


@lru_cache
def get_settings() -> _Settings:
    return _Settings()
