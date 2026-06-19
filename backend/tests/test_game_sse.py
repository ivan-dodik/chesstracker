# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Tests for game SSE events — CRUD must publish real-time notifications."""

import json
from datetime import UTC, datetime

import pytest
from httpx import AsyncClient

from app.services.sse_events import SSEEvents
from app.services.sse_service import subscribe, unsubscribe


@pytest.mark.asyncio
async def test_create_game_publishes_event(client: AsyncClient, admin_token: str):
    """POST /api/tournaments/{id}/games must publish GAME_CREATED SSE event."""
    from app.models import Player, Tournament
    from tests.conftest import TestSessionLocal

    async with TestSessionLocal() as session:
        t = Tournament(
            name="Game SSE Tournament", start_date=datetime(2026, 7, 1, tzinfo=UTC),
            end_date=datetime(2026, 7, 10, tzinfo=UTC),
            location="Moscow", type="classic", rounds=7, status="active",
        )
        session.add(t)
        await session.flush()
        p1 = Player(name="White Player", rating=1500, city="Moscow")
        p2 = Player(name="Black Player", rating=1400, city="SPB")
        session.add_all([p1, p2])
        await session.flush()
        tournament_id = t.id
        white_id = p1.id
        black_id = p2.id
        await session.commit()

    queue = await subscribe("all")
    try:
        response = await client.post(
            f"/api/tournaments/{tournament_id}/games",
            json={
                "game_round": 1,
                "white_player_id": white_id,
                "black_player_id": black_id,
                "result": "1-0",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201

        messages = []
        while not queue.empty():
            messages.append(await queue.get())

        game_events = [m for m in messages if m["event"] == SSEEvents.GAME_CREATED]
        assert len(game_events) >= 1, "Should publish GAME_CREATED event"
        data = json.loads(game_events[0]["data"])
        assert data["data"]["tournament_id"] == tournament_id
    finally:
        unsubscribe("all", queue)


@pytest.mark.asyncio
async def test_update_game_publishes_event(client: AsyncClient, admin_token: str):
    """PUT /api/games/{id} must publish GAME_UPDATED SSE event (not game_result_updated)."""
    from app.models import Game, Player, Tournament
    from tests.conftest import TestSessionLocal

    async with TestSessionLocal() as session:
        t = Tournament(
            name="Update Game Tournament", start_date=datetime(2026, 7, 1, tzinfo=UTC),
            end_date=datetime(2026, 7, 10, tzinfo=UTC),
            location="Moscow", type="classic", rounds=7, status="active",
        )
        session.add(t)
        await session.flush()
        p1 = Player(name="White U", rating=1500, city="Moscow")
        p2 = Player(name="Black U", rating=1400, city="SPB")
        session.add_all([p1, p2])
        await session.flush()
        game = Game(
            tournament_id=t.id, game_round=1,
            white_player_id=p1.id, black_player_id=p2.id,
        )
        session.add(game)
        await session.commit()
        await session.refresh(game)
        game_id = game.id

    queue = await subscribe("all")
    try:
        response = await client.put(
            f"/api/games/{game_id}",
            json={"result": "1-0"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200

        messages = []
        while not queue.empty():
            messages.append(await queue.get())

        game_events = [m for m in messages if m["event"] == SSEEvents.GAME_UPDATED]
        assert len(game_events) >= 1, (
            "Should publish GAME_UPDATED event (not game_result_updated)"
        )
        data = json.loads(game_events[0]["data"])
        assert data["data"]["result"] == "1-0"
    finally:
        unsubscribe("all", queue)


@pytest.mark.asyncio
async def test_delete_game_publishes_event(client: AsyncClient, admin_token: str):
    """DELETE /api/games/{id} must publish GAME_DELETED SSE event."""
    from app.models import Game, Player, Tournament
    from tests.conftest import TestSessionLocal

    async with TestSessionLocal() as session:
        t = Tournament(
            name="Delete Game Tournament", start_date=datetime(2026, 7, 1, tzinfo=UTC),
            end_date=datetime(2026, 7, 10, tzinfo=UTC),
            location="Moscow", type="classic", rounds=7, status="active",
        )
        session.add(t)
        await session.flush()
        p1 = Player(name="White D", rating=1500, city="Moscow")
        p2 = Player(name="Black D", rating=1400, city="SPB")
        session.add_all([p1, p2])
        await session.flush()
        game = Game(
            tournament_id=t.id, game_round=1,
            white_player_id=p1.id, black_player_id=p2.id,
        )
        session.add(game)
        await session.commit()
        await session.refresh(game)
        game_id = game.id
        tournament_id = t.id

    queue = await subscribe("all")
    try:
        response = await client.delete(
            f"/api/games/{game_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 204

        messages = []
        while not queue.empty():
            messages.append(await queue.get())

        game_events = [m for m in messages if m["event"] == SSEEvents.GAME_DELETED]
        assert len(game_events) >= 1, "Should publish GAME_DELETED event"
        data = json.loads(game_events[0]["data"])
        assert data["data"]["game_id"] == game_id
        assert data["data"]["tournament_id"] == tournament_id
    finally:
        unsubscribe("all", queue)
