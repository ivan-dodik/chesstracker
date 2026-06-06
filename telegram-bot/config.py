"""Telegram bot configuration via pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Bot configuration."""

    TG_BOT_TOKEN: str = ""
    BACKEND_URL: str = "http://backend:8000"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
