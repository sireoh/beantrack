"""Typed application settings, loaded from environment variables and `.env`."""

from functools import lru_cache
from pathlib import Path

from cryptography.fernet import Fernet
from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime configuration. Field names map to upper-case env vars (DATA_DIR, ...)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Storage
    data_dir: Path = Path("./data")
    database_name: str = "beantrack.db"

    # Discord OAuth2
    discord_client_id: str
    discord_client_secret: SecretStr
    discord_redirect_uri: str

    # External APIs
    omdb_api_key: SecretStr

    # Fernet key used to encrypt Discord OAuth tokens at rest.
    encryption_key: SecretStr

    # Backblaze B2 (used by Litestream, not by the app itself; loaded so one .env drives both)
    b2_key_id: str = ""
    b2_application_key: SecretStr = SecretStr("")
    b2_bucket_name: str = ""
    b2_endpoint: str = ""

    # Sessions / cookies
    session_ttl_days: int = 30
    session_cookie_name: str = "beantrack_session"
    cookie_secure: bool = True
    # Where the browser is sent after a successful Discord login.
    frontend_url: str = "/"
    # Browser origins allowed to call the API with credentials (the SvelteKit frontend).
    # In .env, as JSON: CORS_ORIGINS=["http://127.0.0.1:5173"]
    cors_origins: list[str] = ["http://127.0.0.1:5173", "http://localhost:5173"]

    @field_validator("encryption_key")
    @classmethod
    def _must_be_fernet_key(cls, value: SecretStr) -> SecretStr:
        # Raises ValueError (surfaced as a ValidationError) if the key is malformed.
        Fernet(value.get_secret_value().encode())
        return value

    @property
    def database_path(self) -> Path:
        return self.data_dir / self.database_name

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.database_path.as_posix()}"


@lru_cache
def get_settings() -> Settings:
    """Process-wide settings singleton (reads `.env` from the current working directory)."""
    return Settings()  # type: ignore[call-arg]  # required fields come from the environment
