from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses .env file for defaults.
    """

    # Security
    secret_key: str = Field(default="your-secret-key", description="JWT secret key")

    # Environment
    dev_mode: bool = Field(
        default=False, description="Enable development mode (e.g., debug logs)"
    )

    # Database
    database_uri: str = Field(
        default="postgresql://user:pass@localhost/db",
        description="PostgreSQL connection URI (e.g., postgresql://user:pass@host/db)",
    )

    # External APIs
    omdb_api_key: str = Field(
        default="your-omdb-key", description="OMDB API key for movie/TV data"
    )

    # Server
    port: int = Field(default=8000, description="Server port")

    # Optional: CORS origins
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"], description="Allowed CORS origins"
    )

    # Pydantic config to load from .env
    class Config:
        env_file = ".env"  # Path to your .env file
        env_file_encoding = "utf-8"
        case_sensitive = False  # Allow case-insensitive env vars
