# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Tests for player tournaments API endpoint."""

import datetime

import pytest
from httpx import AsyncClient

from app.models import Game, Player, Tournament


@pytest.mark.asyncio
async def test_get_player_tournaments_success(client: AsyncClient, user_token: str):
    """Test GET /api/players/{id}/tournaments returns player's tournaments."""
    from tests.conftest import TestSessionLocal

    async with TestSessionLocal() as session:
        player1 = Player(name="Player One", rating=2500, city="Moscow")
        player2 = Player(name="Player Two", rating=2400, city="SPB")
        session.add_all([player1, player2])
        await session.commit()

        t1 = Tournament(
            name="Tournament A", start_date=datetime.datetime(2026, 1, 1),
            end_date=datetime.datetime(2026, 1, 7), rounds=3, type="classic",
            location="Moscow", status="completed",
        )
        t2 = Tournament(
            name="Tournament B", start_date=datetime.datetime(2026, 2, 1),
            end_date=datetime.datetime(2026, 2, 7), rounds=5, type="rapid",
            location="SPB", status="active",
        )
        session.add_all([t1, t2])
        await session.commit()

        game1 = Game(
            tournament_id=t1.id, game_round=1,
            white_player_id=player1.id, black_player_id=player2.id,
            result="1-0", played_at=datetime.datetime(2026, 1, 2),
        )
        game2 = Game(
            tournament_id=t2.id, game_round=1,
            white_player_id=player1.id, black_player_id=player2.id,
            result="½-½", played_at=datetime.datetime(2026, 2, 2),
        )
        session.add_all([game1, game2])
        await session.commit()

        player_id = player1.id

    response = await client.get(
        f"/api/players/{player_id}/tournaments",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    names = [t["name"] for t in data["items"]]
    assert "Tournament A" in names
    assert "Tournament B" in names


@pytest.mark.asyncio
async def test_get_player_tournaments_unauthorized(client: AsyncClient):
    """Test GET /api/players/{id}/tournaments without token returns 401."""
    response = await client.get("/api/players/1/tournaments")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_player_tournaments_empty(client: AsyncClient, user_token: str):
    """Test GET /api/players/{id}/tournaments for player with no games."""
    from tests.conftest import TestSessionLocal

    async with TestSessionLocal() as session:
        player = Player(name="Lonely Player", rating=2000, city="Tomsk")
        session.add(player)
        await session.commit()
        player_id = player.id

    response = await client.get(
        f"/api/players/{player_id}/tournaments",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []
