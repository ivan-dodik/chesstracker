"""Handler for the /start command."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message with instructions."""
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Привет, {user.first_name or 'шахматист'}!\n\n"
        "Добро пожаловать в Chess Tracker Bot.\n\n"
        "Я буду уведомлять тебя о новых партиях и результатах турниров.\n\n"
        "Команды:\n"
        "/subscribe — подписаться на уведомления\n"
        "/unsubscribe — отписаться от уведомлений\n"
        "/start — показать это сообщение"
    )
    logger.info("User %s (%s) sent /start", user.id, user.username)