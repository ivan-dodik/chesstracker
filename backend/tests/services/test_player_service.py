# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Unit tests for player service.

Tests business logic for player CRUD operations directly via service functions.
Uses SQLite (aiosqlite) for isolated, fast tests.
"""

import pytest

from app.schemas.player import PlayerCreate
from app.services.player_service import (
    create_player,
    delete_player,
    get_player,
    get_players,
    update_player,
)


@pytest.mark.asyncio
class TestPlayerService:
    """Tests for player service CRUD operations."""

    async def test_create_and_get_player(self, db_session, sample_admin):
        """Test creating a player and retrieving it by ID."""
        data = PlayerCreate(name="Alice", rating=1800, city="Moscow")
        player = await create_player(db_session, data, user_id=sample_admin.id)

        assert player.id is not None
        assert player.name == "Alice"
        assert player.rating == 1800
        assert player.city == "Moscow"

        # Verify retrieval
        fetched = await get_player(db_session, player.id)
        assert fetched is not None
        assert fetched.name == "Alice"

    async def test_get_players_pagination_and_search(self, db_session, sample_admin):
        """Test paginated players list with search filters."""
        # Create multiple players
        players_data = [
            PlayerCreate(name="Bob", rating=1700, city="Moscow"),
            PlayerCreate(name="Charlie", rating=1600, city="Saint Petersburg"),
            PlayerCreate(name="David", rating=1900, city="Moscow"),
        ]
        for data in players_data:
            await create_player(db_session, data, user_id=sample_admin.id)

        # Test pagination: page 1, per_page 2
        result, total = await get_players(db_session, page=1, per_page=2)
        assert len(result) == 2
        assert total == 3

        # Test search by name
        result, total = await get_players(db_session, name="Bob")
        assert len(result) == 1
        assert result[0].name == "Bob"

        # Test search by city
        result, total = await get_players(db_session, city="Moscow")
        assert len(result) == 2

        # Test filter by rating range
        result, total = await get_players(db_session, rating_min=1700, rating_max=1800)
        assert len(result) == 1
        assert result[0].name == "Bob"

    async def test_update_and_delete_player(self, db_session, sample_admin):
        """Test updating player info and deleting a player."""
        data = PlayerCreate(name="Eve", rating=1500, city="Kazan")
        player = await create_player(db_session, data, user_id=sample_admin.id)

        # Update player
        update_data = PlayerCreate(name="Eve Updated", rating=1550, city="Sochi")
        updated = await update_player(db_session, player.id, update_data, user_id=sample_admin.id)
        assert updated is not None
        assert updated.name == "Eve Updated"
        assert updated.rating == 1550

        # Delete player
        deleted = await delete_player(db_session, player.id, user_id=sample_admin.id)
        assert deleted is True

        # Verify deleted
        fetched = await get_player(db_session, player.id)
        assert fetched is None

        # Delete nonexistent player
        deleted = await delete_player(db_session, 99999, user_id=sample_admin.id)
        assert deleted is False
