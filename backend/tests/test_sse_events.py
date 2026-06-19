# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Tests for SSE event type constants."""

from app.services.sse_events import SSEEvents


def test_all_event_types_are_strings():
    """All SSEEvents attributes must be non-empty strings."""
    event_types = [
        SSEEvents.PLAYER_CREATED,
        SSEEvents.PLAYER_UPDATED,
        SSEEvents.PLAYER_DELETED,
        SSEEvents.TOURNAMENT_CREATED,
        SSEEvents.TOURNAMENT_UPDATED,
        SSEEvents.TOURNAMENT_DELETED,
        SSEEvents.GAME_CREATED,
        SSEEvents.GAME_UPDATED,
        SSEEvents.GAME_DELETED,
        SSEEvents.RATING_UPDATED,
    ]
    for et in event_types:
        assert isinstance(et, str)
        assert len(et) > 0


def test_no_duplicate_event_types():
    """All event type values must be unique."""
    event_types = [
        SSEEvents.PLAYER_CREATED,
        SSEEvents.PLAYER_UPDATED,
        SSEEvents.PLAYER_DELETED,
        SSEEvents.TOURNAMENT_CREATED,
        SSEEvents.TOURNAMENT_UPDATED,
        SSEEvents.TOURNAMENT_DELETED,
        SSEEvents.GAME_CREATED,
        SSEEvents.GAME_UPDATED,
        SSEEvents.GAME_DELETED,
        SSEEvents.RATING_UPDATED,
    ]
    assert len(event_types) == len(set(event_types))


def test_event_types_match_frontend_listeners():
    """Event type values must match the names used in frontend addEventListener calls."""
    expected = {
        "player_created",
        "player_updated",
        "player_deleted",
        "tournament_created",
        "tournament_updated",
        "tournament_deleted",
        "game_created",
        "game_updated",
        "game_deleted",
        "rating_updated",
    }
    actual = {
        SSEEvents.PLAYER_CREATED,
        SSEEvents.PLAYER_UPDATED,
        SSEEvents.PLAYER_DELETED,
        SSEEvents.TOURNAMENT_CREATED,
        SSEEvents.TOURNAMENT_UPDATED,
        SSEEvents.TOURNAMENT_DELETED,
        SSEEvents.GAME_CREATED,
        SSEEvents.GAME_UPDATED,
        SSEEvents.GAME_DELETED,
        SSEEvents.RATING_UPDATED,
    }
    assert actual == expected
