"""Unit tests for activity log service.

Tests creating activity log entries and fetching paginated logs.
"""

import pytest

from app.services.activity_log_service import get_activity_log, log_activity


@pytest.mark.asyncio
class TestActivityLogService:
    """Tests for activity log service."""

    async def test_create_and_get_log(self, db_session, sample_admin):
        """Test creating a log entry and retrieving it."""
        log = await log_activity(
            db_session,
            user_id=sample_admin.id,
            action="create",
            entity_type="player",
            entity_id=1,
            new_values={"name": "Test Player", "rating": 1500},
        )
        assert log.id is not None
        assert log.action == "create"
        assert log.entity_type == "player"

        # Retrieve log
        logs, total = await get_activity_log(db_session)
        assert total == 1
        assert len(logs) == 1
        assert logs[0]["action"] == "create"
        assert logs[0]["new_values"]["name"] == "Test Player"

    async def test_get_log_pagination_and_filter(self, db_session, sample_admin, sample_user):
        """Test pagination and filtering of activity log."""
        for i in range(5):
            await log_activity(
                db_session,
                user_id=sample_admin.id if i % 2 == 0 else sample_user.id,
                action="update" if i % 2 == 0 else "delete",
                entity_type="tournament",
                entity_id=i,
            )

        # Test pagination
        logs, total = await get_activity_log(db_session, page=1, per_page=2)
        assert len(logs) == 2
        assert total == 5

        # Test filter by action
        logs, total = await get_activity_log(db_session, action="delete")
        assert total == 2

        # Test filter by user
        logs, total = await get_activity_log(db_session, user_id=sample_admin.id)
        assert total == 3
