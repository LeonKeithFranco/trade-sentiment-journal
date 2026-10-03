from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field, PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class _DbSettings(BaseModel):
    """Database connection settings loaded from environment variables.

    Attributes:
        host: The database server hostname.
        user: The database username.
        password: The database password.
        name: The database name.
        port: The database server port.
    """

    host: str = "localhost"
    user: str
    password: str
    name: str
    port: int = 5432

    @computed_field
    @property
    def url(self) -> PostgresDsn:
        """Build the async PostgreSQL DSN from the individual connection settings.

        Returns:
            PostgresDSN: The fully assembled connection URL using the asyncpg driver.
        """
        return PostgresDsn(
            MultiHostUrl.build(
                scheme="postgresql+asyncpg",
                username=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                path=self.name,
            )
        )


class _AppSettings(BaseModel):
    """General application settings.

    Attributes:
        name: The display name of the application.
        debug: Whether to enable debug mode.
    """

    name: str = "App Name"
    debug: bool = True


class _SecuritySettings(BaseModel):
    """Settings controlling password hashing and JWT token behaviour.

    Attributes:
        pepper_secret: The secret pepper appended to passwords before hashing.
        token_secret: The secret key used to sign JWT tokens.
        access_token_expire_minutes: The number of minutes before an access token expires.
        refresh_token_expire_days: The number of days before a refresh token expires.
    """

    pepper_secret: str = Field(
        min_length=32,
    )
    token_secret: str = Field(
        min_length=64,
    )
    access_token_expire_minutes: int = Field(
        ge=1,
    )
    refresh_token_expire_days: int = Field(
        ge=1,
    )


class _Settings(BaseSettings):
    """Backend application settings loaded from environment variables or .env.

    Attributes:
        db: Database connection settings.
        app: General application settings.
        security: Password hashing and token settings.
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

    db: _DbSettings = Field(default_factory=_DbSettings)
    app: _AppSettings = Field(default_factory=_AppSettings)
    security: _SecuritySettings = Field(default_factory=_SecuritySettings)


@lru_cache
def get_settings() -> _Settings:
    """Return the cached application settings singleton.

    Returns:
        _Settings: The backend settings instance.
    """
    return _Settings()
