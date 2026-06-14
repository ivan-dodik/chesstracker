# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Handlers for /subscribe and /unsubscribe commands."""

import json
import logging
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

_SUBSCRIBERS_FILE = Path(__file__).resolve().parent.parent / "subscribers.json"


def _load_subscribers() -> set[int]:
    """Load subscribed chat IDs from a JSON file."""
    if not _SUBSCRIBERS_FILE.exists():
        return set()
    try:
        with open(_SUBSCRIBERS_FILE) as f:
            return set(json.load(f))
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to load subscribers: %s", exc)
        return set()


def _save_subscribers(subscribers: set[int]) -> None:
    """Save subscribed chat IDs to a JSON file."""
    try:
        with open(_SUBSCRIBERS_FILE, "w") as f:
            json.dump(list(subscribers), f)
    except OSError as exc:
        logger.error("Failed to save subscribers: %s", exc)


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Subscribe the current chat to notifications."""
    chat_id = update.effective_chat.id
    subscribers = _load_subscribers()

    if chat_id in subscribers:
        await update.message.reply_text("✅ Ты уже подписан на уведомления.")
        return

    subscribers.add(chat_id)
    _save_subscribers(subscribers)
    await update.message.reply_text(
        "✅ Ты подписан на уведомления!\n"
        "Я буду присылать тебе новые результаты партий."
    )
    logger.info("Chat %s subscribed", chat_id)


async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Unsubscribe the current chat from notifications."""
    chat_id = update.effective_chat.id
    subscribers = _load_subscribers()

    if chat_id not in subscribers:
        await update.message.reply_text("❌ Ты не был подписан на уведомления.")
        return

    subscribers.discard(chat_id)
    _save_subscribers(subscribers)
    await update.message.reply_text("❌ Ты отписан от уведомлений.")
    logger.info("Chat %s unsubscribed", chat_id)


def get_subscribed_chats() -> set[int]:
    """Return the set of subscribed chat IDs (used by notifier)."""
    return _load_subscribers()
