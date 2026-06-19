# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Tests for player SSE events — CRUD must publish real-time notifications."""

import json

import pytest
from httpx import AsyncClient

from app.services.sse_events import SSEEvents
from app.services.sse_service import subscribe, unsubscribe


@pytest.mark.asyncio
async def test_create_player_publishes_event(client: AsyncClient, admin_token: str):
    """POST /api/players must publish PLAYER_CREATED SSE event."""
    queue = await subscribe("all")
    try:
        response = await client.post(
            "/api/players",
            json={"name": "SSE Player", "rating": 1500, "city": "Moscow"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201

        message = await queue.get()
        assert message["event"] == SSEEvents.PLAYER_CREATED
        data = json.loads(message["data"])
        assert data["player_name"] == "SSE Player"
        assert data["rating"] == 1500
    finally:
        unsubscribe("all", queue)


@pytest.mark.asyncio
async def test_update_player_publishes_event(client: AsyncClient, admin_token: str):
    """PUT /api/players/{id} must publish PLAYER_UPDATED SSE event."""
    from app.models import Player
    from tests.conftest import TestSessionLocal

    async with TestSessionLocal() as session:
        player = Player(name="Old Name", rating=1500, city="Moscow")
        session.add(player)
        await session.commit()
        await session.refresh(player)
        player_id = player.id

    queue = await subscribe("all")
    try:
        response = await client.put(
            f"/api/players/{player_id}",
            json={"name": "New Name", "rating": 1600, "city": "SPB"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200

        message = await queue.get()
        assert message["event"] == SSEEvents.PLAYER_UPDATED
        data = json.loads(message["data"])
        assert data["player_name"] == "New Name"
    finally:
        unsubscribe("all", queue)


@pytest.mark.asyncio
async def test_update_player_rating_publishes_rating_event(client: AsyncClient, admin_token: str):
    """PUT /api/players/{id} with rating change must publish RATING_UPDATED SSE event."""
    from app.models import Player
    from tests.conftest import TestSessionLocal

    async with TestSessionLocal() as session:
        player = Player(name="Rating Player", rating=1500, city="Moscow")
        session.add(player)
        await session.commit()
        await session.refresh(player)
        player_id = player.id

    queue = await subscribe("all")
    try:
        response = await client.put(
            f"/api/players/{player_id}",
            json={"name": "Rating Player", "rating": 1700, "city": "Moscow"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200

        # Collect all messages from the queue
        messages = []
        while not queue.empty():
            messages.append(await queue.get())

        rating_events = [m for m in messages if m["event"] == SSEEvents.RATING_UPDATED]
        assert len(rating_events) >= 1, "Should publish RATING_UPDATED when rating changes"
        data = json.loads(rating_events[0]["data"])
        assert data["old_rating"] == 1500
        assert data["new_rating"] == 1700
    finally:
        unsubscribe("all", queue)


@pytest.mark.asyncio
async def test_delete_player_publishes_event(client: AsyncClient, admin_token: str):
    """DELETE /api/players/{id} must publish PLAYER_DELETED SSE event."""
    from app.models import Player
    from tests.conftest import TestSessionLocal

    async with TestSessionLocal() as session:
        player = Player(name="Delete Me", rating=1200, city="Kazan")
        session.add(player)
        await session.commit()
        await session.refresh(player)
        player_id = player.id

    queue = await subscribe("all")
    try:
        response = await client.delete(
            f"/api/players/{player_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 204

        message = await queue.get()
        assert message["event"] == SSEEvents.PLAYER_DELETED
        data = json.loads(message["data"])
        assert data["player_id"] == player_id
        assert data["player_name"] == "Delete Me"
    finally:
        unsubscribe("all", queue)
