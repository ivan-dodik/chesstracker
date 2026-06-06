"""Chess Tracker Telegram Bot — entry point."""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Start the bot."""
    logger.info("Chess Tracker Bot starting...")


if __name__ == "__main__":
    main()