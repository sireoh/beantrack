"""Typed application settings, loaded from environment variables and `.env`."""

import ipaddress
from datetime import time
from functools import lru_cache
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
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
    # TMDB "API Read Access Token" (v4 bearer token). Only the Discover pages need it.
    tmdb_bearer_token: SecretStr = SecretStr("")
    # How long a cached TMDB discover page is served before it is fetched again.
    discover_cache_hours: int = 24

    # Reverse proxies allowed to report the client's IP (X-Forwarded-For / X-Real-IP):
    # comma-separated IPs or CIDR ranges. Uvicorn reads the same variable in Docker.
    # From anyone else the headers are ignored and the connection's own IP is used.
    forwarded_allow_ips: str = "127.0.0.1"

    # Fernet key used to encrypt Discord OAuth tokens at rest.
    encryption_key: SecretStr

    # Backblaze B2: manual + daily backups (leave empty to turn backups off)
    b2_key_id: str = ""
    b2_application_key: SecretStr = SecretStr("")
    b2_bucket_name: str = ""

    # Daily backup to B2, run by the API process itself (needs the B2_* values above).
    # Each run costs ~2 B2 Class C calls (authorize + list), well under the free 2,500/day.
    daily_backup_enabled: bool = True
    daily_backup_time: time = time(3, 0)  # HH:MM, in daily_backup_timezone
    # IANA time zone name, e.g. UTC, America/Vancouver, Europe/London. DST is handled.
    daily_backup_timezone: str = "UTC"
    daily_backup_keep: int = 7  # older daily backups are deleted; manual ones never are

    @field_validator("daily_backup_timezone")
    @classmethod
    def _must_be_time_zone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValueError(f"Unknown time zone {value!r}; use a name like America/Vancouver") from exc
        return value

    @property
    def daily_backup_zone(self) -> ZoneInfo:
        return ZoneInfo(self.daily_backup_timezone)

    @field_validator("forwarded_allow_ips")
    @classmethod
    def _must_be_networks(cls, value: str) -> str:
        for item in value.split(","):
            item = item.strip()
            if item and item != "*":
                ipaddress.ip_network(item, strict=False)  # ValueError -> ValidationError
        return value

    @property
    def trusted_proxies(self) -> list[ipaddress.IPv4Network | ipaddress.IPv6Network] | None:
        """Parsed FORWARDED_ALLOW_IPS. None means "*" (trust every peer)."""
        items = [i.strip() for i in self.forwarded_allow_ips.split(",") if i.strip()]
        if "*" in items:
            return None
        return [ipaddress.ip_network(i, strict=False) for i in items]

    @property
    def b2_configured(self) -> bool:
        return bool(
            self.b2_key_id and self.b2_application_key.get_secret_value() and self.b2_bucket_name
        )

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
