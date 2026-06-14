# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Unit tests for game service.

Tests business logic for game CRUD and standings updates.
"""

import pytest

from app.schemas.game import GameCreate, GameResult
from app.services.game_service import (
    create_game,
    delete_game,
    get_games_by_tournament,
    update_game_result,
)


@pytest.mark.asyncio
class TestGameService:
    """Tests for game service CRUD operations."""

    async def test_create_and_get_games(self, db_session, sample_tournament, sample_player):
        """Test creating a game and listing games by tournament."""
        from app.models import Player

        player2 = Player(name="Opponent", rating=1400, city="Lyon")
        db_session.add(player2)
        await db_session.flush()

        data = GameCreate(
            tournament_id=sample_tournament.id,
            game_round=1,
            white_player_id=sample_player.id,
            black_player_id=player2.id,
            result="1-0",
        )
        game = await create_game(db_session, data, user_id=1)

        assert game.id is not None
        assert game.game_round == 1
        assert game.result == "1-0"
        assert game.white_player_id == sample_player.id
        assert game.black_player_id == player2.id

        # Verify listing by tournament
        games, total = await get_games_by_tournament(db_session, sample_tournament.id)
        assert len(games) == 1
        assert total == 1
        assert games[0]["white_player_name"] == "Test Player"
        assert games[0]["black_player_name"] == "Opponent"

    async def test_update_game_result(self, db_session, sample_tournament, sample_player):
        """Test updating a game result."""
        from app.models import Player

        player2 = Player(name="Opponent", rating=1400, city="Lyon")
        db_session.add(player2)
        await db_session.flush()

        data = GameCreate(
            tournament_id=sample_tournament.id, game_round=1,
            white_player_id=sample_player.id, black_player_id=player2.id,
        )
        game = await create_game(db_session, data, user_id=1)
        assert game.result is None  # No result initially

        # Update result
        updated = await update_game_result(
            db_session, game.id, GameResult(result="0-1"), user_id=1,
        )
        assert updated is not None
        assert updated.result == "0-1"

        # Update nonexistent game
        updated = await update_game_result(
            db_session, 99999, GameResult(result="1-0"), user_id=1,
        )
        assert updated is None

    async def test_delete_game(self, db_session, sample_tournament, sample_player):
        """Test deleting a game."""
        from app.models import Player

        player2 = Player(name="Opponent", rating=1400, city="Lyon")
        db_session.add(player2)
        await db_session.flush()

        data = GameCreate(
            tournament_id=sample_tournament.id, game_round=1,
            white_player_id=sample_player.id, black_player_id=player2.id,
        )
        game = await create_game(db_session, data, user_id=1)

        # Delete game
        deleted = await delete_game(db_session, game.id, user_id=1)
        assert deleted is True

        # Verify deletion
        games, total = await get_games_by_tournament(db_session, sample_tournament.id)
        assert total == 0

        # Delete nonexistent game
        deleted = await delete_game(db_session, 99999, user_id=1)
        assert deleted is False
