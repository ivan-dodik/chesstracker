# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Tests for tournament SSE events — CRUD must publish real-time notifications."""

import json
from datetime import UTC, datetime

import pytest
from httpx import AsyncClient

from app.services.sse_events import SSEEvents
from app.services.sse_service import subscribe, unsubscribe


@pytest.mark.asyncio
async def test_create_tournament_publishes_event(client: AsyncClient, admin_token: str):
    """POST /api/tournaments must publish TOURNAMENT_CREATED SSE event."""
    queue = await subscribe("all")
    try:
        response = await client.post(
            "/api/tournaments",
            json={
                "name": "SSE Tournament",
                "start_date": "2026-07-01T00:00:00",
                "end_date": "2026-07-10T00:00:00",
                "location": "Moscow",
                "type": "classic",
                "rounds": 7,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201

        message = await queue.get()
        assert message["event"] == SSEEvents.TOURNAMENT_CREATED
        data = json.loads(message["data"])
        assert data["tournament_name"] == "SSE Tournament"
    finally:
        unsubscribe("all", queue)


@pytest.mark.asyncio
async def test_update_tournament_publishes_event(client: AsyncClient, admin_token: str):
    """PUT /api/tournaments/{id} must publish TOURNAMENT_UPDATED SSE event."""
    from app.models import Tournament
    from tests.conftest import TestSessionLocal

    async with TestSessionLocal() as session:
        t = Tournament(
            name="Old Tournament", start_date=datetime(2026, 7, 1, tzinfo=UTC),
            end_date=datetime(2026, 7, 10, tzinfo=UTC),
            location="Moscow", type="classic", rounds=7, status="active",
        )
        session.add(t)
        await session.commit()
        await session.refresh(t)
        tournament_id = t.id

    queue = await subscribe("all")
    try:
        response = await client.put(
            f"/api/tournaments/{tournament_id}",
            json={
                "name": "Updated Tournament",
                "start_date": "2026-07-01T00:00:00",
                "end_date": "2026-07-10T00:00:00",
                "location": "SPB",
                "type": "blitz",
                "rounds": 5,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200

        message = await queue.get()
        assert message["event"] == SSEEvents.TOURNAMENT_UPDATED
        data = json.loads(message["data"])
        assert data["tournament_name"] == "Updated Tournament"
    finally:
        unsubscribe("all", queue)


@pytest.mark.asyncio
async def test_delete_tournament_publishes_event(client: AsyncClient, admin_token: str):
    """DELETE /api/tournaments/{id} must publish TOURNAMENT_DELETED SSE event."""
    from app.models import Tournament
    from tests.conftest import TestSessionLocal

    async with TestSessionLocal() as session:
        t = Tournament(
            name="Delete Tournament", start_date=datetime(2026, 7, 1, tzinfo=UTC),
            end_date=datetime(2026, 7, 10, tzinfo=UTC),
            location="Kazan", type="classic", rounds=5, status="active",
        )
        session.add(t)
        await session.commit()
        await session.refresh(t)
        tournament_id = t.id

    queue = await subscribe("all")
    try:
        response = await client.delete(
            f"/api/tournaments/{tournament_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 204

        message = await queue.get()
        assert message["event"] == SSEEvents.TOURNAMENT_DELETED
        data = json.loads(message["data"])
        assert data["tournament_id"] == tournament_id
    finally:
        unsubscribe("all", queue)
