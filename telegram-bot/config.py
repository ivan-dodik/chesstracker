# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Telegram bot configuration via pydantic-settings."""

import re

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Bot configuration."""

    TG_BOT_TOKEN: str = ""
    BACKEND_URL: str = "http://backend:8000"

    model_config = {"env_file": ".env", "extra": "ignore"}

    def is_token_valid(self) -> bool:
        """Check if the token is set and not a placeholder.

        Returns:
            True if the token looks like a real Telegram bot token.
        """
        if not self.TG_BOT_TOKEN:
            return False

        # Common placeholder values from .env.example
        placeholders = {
            "your-telegram-bot-token",
            "your_bot_token",
            "token",
            "bot_token",
            "changeme",
            "change-me",
        }
        if self.TG_BOT_TOKEN.strip().lower() in placeholders:
            return False

        # Telegram bot tokens have the format: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
        if not re.match(r"^\d+:[A-Za-z0-9_-]+$", self.TG_BOT_TOKEN):
            return False

        return True


settings = Settings()
