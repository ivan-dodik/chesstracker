"""Unit tests for tournament service.

Tests business logic for tournament CRUD and standings calculation.
"""

import pytest

from app.schemas.tournament import TournamentCreate
from app.services.tournament_service import (
    create_tournament,
    delete_tournament,
    get_standings,
    get_tournament,
    get_tournaments,
    update_tournament,
)


@pytest.mark.asyncio
class TestTournamentService:
    """Tests for tournament service CRUD and standings."""

    async def test_create_and_get_tournament(self, db_session, sample_admin):
        """Test creating a tournament and retrieving it by ID."""
        from datetime import datetime

        data = TournamentCreate(
            name="Grand Prix",
            start_date=datetime(2026, 5, 1),
            end_date=datetime(2026, 5, 10),
            location="Moscow",
            rounds=7,
            type="blitz",
            status="active",
        )
        tournament = await create_tournament(db_session, data, user_id=sample_admin.id)

        assert tournament.id is not None
        assert tournament.name == "Grand Prix"
        assert tournament.location == "Moscow"
        assert tournament.type == "blitz"

        # Verify retrieval
        fetched = await get_tournament(db_session, tournament.id)
        assert fetched is not None
        assert fetched.name == "Grand Prix"

    async def test_get_tournaments_pagination_and_filter(self, db_session, sample_admin):
        """Test paginated tournaments list with filters."""
        from datetime import datetime

        tournaments_data = [
            TournamentCreate(
                name="Tour A", start_date=datetime(2026, 1, 1), end_date=datetime(2026, 1, 5),
                status="completed",
            ),
            TournamentCreate(
                name="Tour B", start_date=datetime(2026, 2, 1), end_date=datetime(2026, 2, 5),
                status="active",
            ),
            TournamentCreate(
                name="Tour C", start_date=datetime(2026, 3, 1), end_date=datetime(2026, 3, 5),
                status="active",
            ),
        ]
        for data in tournaments_data:
            await create_tournament(db_session, data, user_id=sample_admin.id)

        # Test pagination
        result, total = await get_tournaments(db_session, page=1, per_page=2)
        assert len(result) == 2
        assert total == 3

        # Test filter by status
        result, total = await get_tournaments(db_session, status="active")
        assert len(result) == 2

        result, total = await get_tournaments(db_session, status="completed")
        assert len(result) == 1

    async def test_update_and_delete_tournament_with_standings(self, db_session, sample_admin, sample_player):
        """Test updating a tournament, deleting, and calculating standings."""
        from datetime import datetime

        from app.models import Game

        data = TournamentCreate(
            name="Championship",
            start_date=datetime(2026, 6, 1),
            end_date=datetime(2026, 6, 10),
            location="Paris",
            rounds=3,
        )
        tournament = await create_tournament(db_session, data, user_id=sample_admin.id)

        # Update tournament
        update_data = TournamentCreate(
            name="Championship Updated",
            start_date=datetime(2026, 6, 1),
            end_date=datetime(2026, 6, 10),
            location="Lyon",
            rounds=5,
        )
        updated = await update_tournament(db_session, tournament.id, update_data, user_id=sample_admin.id)
        assert updated is not None
        assert updated.name == "Championship Updated"
        assert updated.location == "Lyon"

        # Create a second player and a game to test standings
        from app.models import Player
        player2 = Player(name="Opponent", rating=1400, city="Lyon")
        db_session.add(player2)
        await db_session.flush()

        game = Game(
            tournament_id=tournament.id, round=1,
            white_player_id=sample_player.id, black_player_id=player2.id,
            result="1-0",
        )
        db_session.add(game)
        await db_session.flush()

        # Test standings calculation
        standings = await get_standings(db_session, tournament.id)
        assert len(standings) == 2
        # sample_player (white) won, so should have 1 point
        winner = [s for s in standings if s["player_id"] == sample_player.id][0]
        assert winner["points"] == 1.0
        assert winner["wins"] == 1

        # Delete tournament
        deleted = await delete_tournament(db_session, tournament.id, user_id=sample_admin.id)
        assert deleted is True

        # Delete nonexistent tournament
        deleted = await delete_tournament(db_session, 99999, user_id=sample_admin.id)
        assert deleted is False
