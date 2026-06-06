"""Unit tests for favorite service.

Tests adding, removing, and listing favorite players.
"""

import pytest

from app.services.favorite_service import add_favorite, get_favorites, remove_favorite


@pytest.mark.asyncio
class TestFavoriteService:
    """Tests for favorite service."""

    async def test_add_and_remove_favorite(self, db_session, sample_user, sample_player):
        """Test adding a favorite and removing it."""
        # Add favorite
        favorite = await add_favorite(db_session, sample_user.id, sample_player.id)
        assert favorite is not None
        assert favorite.user_id == sample_user.id
        assert favorite.player_id == sample_player.id

        # Verify in list
        favorites = await get_favorites(db_session, sample_user.id)
        assert len(favorites) == 1
        assert favorites[0].player_id == sample_player.id

        # Remove favorite
        removed = await remove_favorite(db_session, sample_user.id, sample_player.id)
        assert removed is True

        # Verify removal
        favorites = await get_favorites(db_session, sample_user.id)
        assert len(favorites) == 0

    async def test_add_duplicate_and_remove_nonexistent(self, db_session, sample_user, sample_player):
        """Test duplicate favorite returns None and remove nonexistent returns False."""
        # Add first time
        favorite = await add_favorite(db_session, sample_user.id, sample_player.id)
        assert favorite is not None

        # Add duplicate
        duplicate = await add_favorite(db_session, sample_user.id, sample_player.id)
        assert duplicate is None

        # Remove
        removed = await remove_favorite(db_session, sample_user.id, sample_player.id)
        assert removed is True

        # Remove again (nonexistent)
        removed = await remove_favorite(db_session, sample_user.id, sample_player.id)
        assert removed is False
