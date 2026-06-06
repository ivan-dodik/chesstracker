"""Chess Tracker Telegram Bot — entry point.

Long-polling bot that notifies subscribed users about new games and results.
"""

import logging

from telegram import Update
from telegram.ext import Application, CommandHandler

from config import settings
from handlers.start import start_command
from handlers.subscribe import subscribe_command, unsubscribe_command
from services.notifier import Notifier

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Start the bot with long-polling and background notification task."""
    if not settings.is_token_valid():
        logger.warning(
            "TG_BOT_TOKEN is not set or is a placeholder. "
            "Bot will not start. Set a real token in .env to enable the bot."
        )
        return

    application = Application.builder().token(settings.TG_BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe_command))

    # Background notification task
    notifier = Notifier(application.bot)
    application.job_queue.run_repeating(
        notifier.check_for_updates,
        interval=60,  # seconds
        first=10,  # start after 10 seconds
    )

    logger.info("Chess Tracker Bot started (long-polling mode)")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
