# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""E2E tests: M20 — SSE real-time updates (file checks + API read-only)."""

import os


def _read(path: str) -> str:
    with open(path) as f:
        return f.read()


def test_sse_client_in_template():
    """M20.1 Dashboard template references SSE client."""
    content = _read(os.path.join(os.path.dirname(__file__), "..", "app", "templates", "index.html"))
    assert "EventSource" in content or "sse.js" in content or "sseClient" in content


def test_sse_rating_listener_in_template():
    """M20.2 Dashboard template has rating_updated SSE listener."""
    content = _read(os.path.join(os.path.dirname(__file__), "..", "app", "templates", "index.html"))
    has = any(kw in content for kw in ["rating_updated", "top-rated", "topRated", "top_rated"])
    assert has, "Dashboard should have SSE listener for rating_updated events"


def test_sse_game_listener_in_template():
    """M20.3 Tournament detail template has game event SSE listeners."""
    content = _read(
        os.path.join(
            os.path.dirname(__file__), "..", "app", "templates", "tournaments", "detail.html"
        )
    )
    has = any(
        kw in content
        for kw in ["game_created", "game_result_updated", "loadStandings", "loadGames"]
    )
    assert has, "Tournament detail should have SSE listeners for game events"


def test_sse_service_publishes_events():
    """M20.4 SSE service has publish_event function."""
    content = _read(os.path.join(os.path.dirname(__file__), "..", "app", "services", "sse_service.py"))
    assert "publish_event" in content
    assert "async def publish_event" in content


def test_game_service_publishes_sse():
    """M20.5 game_service.py publishes SSE events on game create/update."""
    content = _read(os.path.join(os.path.dirname(__file__), "..", "app", "services", "game_service.py"))
    assert "publish_event" in content, "game_service should publish SSE events"
    assert "GAME_CREATED" in content, "game_service should use SSEEvents.GAME_CREATED"
    assert "GAME_UPDATED" in content, "game_service should use SSEEvents.GAME_UPDATED"


def test_rating_service_publishes_sse():
    """M20.6 rating_calculation_service publishes SSE on rating change."""
    content = _read(
        os.path.join(
            os.path.dirname(__file__), "..", "app", "services", "rating_calculation_service.py"
        )
    )
    assert "publish_event" in content, "rating service should publish SSE events"
    assert "rating_updated" in content, "should publish rating_updated event"


def test_player_service_publishes_sse():
    """M20.7 player_service.py publishes SSE events on CRUD."""
    content = _read(os.path.join(os.path.dirname(__file__), "..", "app", "services", "player_service.py"))
    assert "publish_event" in content, "player_service should publish SSE events"
    assert "PLAYER_CREATED" in content, "should publish PLAYER_CREATED event"
    assert "PLAYER_UPDATED" in content, "should publish PLAYER_UPDATED event"
    assert "PLAYER_DELETED" in content, "should publish PLAYER_DELETED event"
    assert "RATING_UPDATED" in content, "should publish RATING_UPDATED on rating change"


def test_tournament_service_publishes_sse():
    """M20.8 tournament_service.py publishes SSE events on CRUD."""
    content = _read(os.path.join(os.path.dirname(__file__), "..", "app", "services", "tournament_service.py"))
    assert "publish_event" in content, "tournament_service should publish SSE events"
    assert "TOURNAMENT_CREATED" in content
    assert "TOURNAMENT_UPDATED" in content
    assert "TOURNAMENT_DELETED" in content


def test_sse_events_constants_exist():
    """M20.9 sse_events.py defines all event type constants."""
    content = _read(os.path.join(os.path.dirname(__file__), "..", "app", "services", "sse_events.py"))
    assert "PLAYER_CREATED" in content
    assert "TOURNAMENT_CREATED" in content
    assert "GAME_CREATED" in content
    assert "GAME_UPDATED" in content
    assert "GAME_DELETED" in content
    assert "RATING_UPDATED" in content
