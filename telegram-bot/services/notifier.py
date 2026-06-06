"""Background notifier — polls backend for new games and sends notifications."""

import logging

from telegram import Bot
from telegram.constants import ParseMode

from handlers.subscribe import get_subscribed_chats
from services.api_client import ApiClient

logger = logging.getLogger(__name__)

RESULT_EMOJI = {
    "1-0": "♟ 1-0",
    "0-1": "0-1 ♟",
    "½-½": "½-½",
}


class Notifier:
    """Periodically polls backend and notifies subscribed users about new games."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.api = ApiClient()
        self._known_games: set[int] = set()

    async def check_for_updates(self, context=None) -> None:
        """Check for new games in active tournaments and notify subscribers."""
        try:
            tournaments = await self.api.get_active_tournaments()
            if not tournaments:
                return

            for tournament in tournaments:
                await self._check_tournament(tournament)
        except Exception as exc:
            logger.error("Notifier error: %s", exc)

    async def _check_tournament(self, tournament: dict) -> None:
        """Check a single tournament for new games."""
        tournament_id = tournament["id"]
        tournament_name = tournament.get("name", "Unknown")
        games = await self.api.get_tournament_games(tournament_id)

        new_games = [g for g in games if g["id"] not in self._known_games]
        if not new_games:
            return

        self._known_games.update(g["id"] for g in new_games)
        subscribers = get_subscribed_chats()
        if not subscribers:
            return

        message = self._format_message(tournament_name, new_games)
        for chat_id in subscribers:
            try:
                await self.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)
            except Exception as exc:
                logger.warning("Failed to send to chat %s: %s", chat_id, exc)

    def _format_message(self, tournament_name: str, games: list[dict]) -> str:
        """Format notification message with new game results."""
        lines = [f"🏆 <b>{tournament_name}</b>", "Новые партии:", ""]
        for game in games:
            white = game.get("white_player_name", "?")
            black = game.get("black_player_name", "?")
            result = game.get("result", "?")
            icon = RESULT_EMOJI.get(result, result)
            lines.append(f"{white} vs {black} — {icon}")
            if game.get("round"):
                lines[-1] += f" (тур {game['round']})"
        return "\n".join(lines)
