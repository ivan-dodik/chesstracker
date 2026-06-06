"""Application configuration via pydantic-settings."""

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://ct_user:ct_password@localhost:5432/ct_database"

    # Security
    SECRET_KEY: str = "change-me-to-a-random-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Telegram
    TG_BOT_TOKEN: str = ""

    # Backend
    BACKEND_URL: str = "http://backend:8000"
    DEBUG: bool = True

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v: str | bool) -> bool:
        """Allow DEBUG to be set as string 'true'/'false' or any truthy/falsy value."""
        if isinstance(v, bool):
            return v
        return v.lower() in ("true", "1", "yes")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
