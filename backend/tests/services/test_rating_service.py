"""Unit tests for rating service.

Tests rating history retrieval with date filtering.
"""

from datetime import date

import pytest

from app.services.rating_service import get_rating_history


@pytest.mark.asyncio
class TestRatingService:
    """Tests for rating service."""

    async def test_get_rating_history_with_date_filter(self, db_session, sample_player):
        """Test getting rating history with date filters."""
        from app.models import RatingHistory

        # Create rating history entries
        entries = [
            RatingHistory(player_id=sample_player.id, rating=1500, date=date(2026, 1, 1)),
            RatingHistory(player_id=sample_player.id, rating=1520, date=date(2026, 2, 1)),
            RatingHistory(player_id=sample_player.id, rating=1540, date=date(2026, 3, 1)),
        ]
        for entry in entries:
            db_session.add(entry)
        await db_session.flush()

        # Get all history
        history = await get_rating_history(db_session, sample_player.id)
        assert len(history) == 3
        assert history[0].rating == 1500  # Ascending order
        assert history[-1].rating == 1540

        # Filter by date range
        history = await get_rating_history(
            db_session, sample_player.id,
            date_from=date(2026, 2, 1), date_to=date(2026, 2, 28),
        )
        assert len(history) == 1
        assert history[0].rating == 1520

    async def test_get_rating_history_empty(self, db_session):
        """Test getting rating history for a player with no history."""
        from app.models import Player

        player = Player(name="No History", rating=1500)
        db_session.add(player)
        await db_session.flush()

        history = await get_rating_history(db_session, player.id)
        assert len(history) == 0
