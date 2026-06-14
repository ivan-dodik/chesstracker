# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

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

    @field_validator("SECRET_KEY", mode="after")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate SECRET_KEY: warn if default, enforce minimum length."""
        if v == "change-me-to-a-random-secret-key":
            import warnings
            warnings.warn(
                "SECRET_KEY is set to the default value! "
                "Change it in .env or environment variables for production.",
                stacklevel=2,
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    # Telegram
    TG_BOT_TOKEN: str = ""

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:8000"]

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
