"""Unit tests for stats service.

Tests head-to-head, top-rated, and overall stats.
"""

from datetime import datetime

import pytest

from app.services.stats_service import get_head_to_head, get_overall_stats, get_top_rated


@pytest.mark.asyncio
class TestStatsService:
    """Tests for stats service."""

    async def test_top_rated_with_ties(self, db_session, sample_admin):
        """Test top-rated players with identical ratings."""
        from app.schemas.player import PlayerCreate
        from app.services.player_service import create_player

        players_data = [
            PlayerCreate(name="Alpha", rating=1800),
            PlayerCreate(name="Beta", rating=1800),
            PlayerCreate(name="Gamma", rating=1700),
        ]
        for data in players_data:
            await create_player(db_session, data, user_id=sample_admin.id)

        top = await get_top_rated(db_session, limit=2)
        assert len(top) == 2
        assert top[0].rating >= top[1].rating

    async def test_get_overall_stats(self, db_session, sample_player, sample_tournament):
        """Test overall stats calculation for a player with games."""
        from app.models import Game, Player

        player2 = Player(name="Rival", rating=1400)
        db_session.add(player2)
        await db_session.flush()

        games = [
            Game(tournament_id=sample_tournament.id, game_round=1,
                 white_player_id=sample_player.id, black_player_id=player2.id, result="1-0"),
            Game(tournament_id=sample_tournament.id, game_round=2,
                 white_player_id=player2.id, black_player_id=sample_player.id, result="1-0"),
            Game(tournament_id=sample_tournament.id, game_round=3,
                 white_player_id=sample_player.id, black_player_id=player2.id, result="½-½"),
        ]
        for g in games:
            db_session.add(g)
        await db_session.flush()

        stats = await get_overall_stats(db_session, sample_player.id)
        assert stats["total_games"] == 3
        assert stats["wins"] == 1
        assert stats["losses"] == 1
        assert stats["draws"] == 1
        assert stats["win_rate"] == round(1 / 3 * 100, 1)

    async def test_head_to_head(self, db_session, sample_player):
        """Test head-to-head stats between two players."""
        from app.models import Game, Player, Tournament

        tournament = Tournament(name="H2H Tour", start_date=datetime(2026, 1, 1), end_date=datetime(2026, 1, 5))
        db_session.add(tournament)
        await db_session.flush()

        player2 = Player(name="Rival", rating=1400)
        db_session.add(player2)
        await db_session.flush()

        games = [
            Game(tournament_id=tournament.id, game_round=1,
                 white_player_id=sample_player.id, black_player_id=player2.id, result="1-0"),
            Game(tournament_id=tournament.id, game_round=2,
                 white_player_id=sample_player.id, black_player_id=player2.id, result="1-0"),
        ]
        for g in games:
            db_session.add(g)
        await db_session.flush()

        h2h = await get_head_to_head(db_session, sample_player.id, player2.id)
        assert h2h["total_games"] == 2
        assert h2h["player1_wins"] == 2
        assert h2h["player2_wins"] == 0
        assert h2h["draws"] == 0
