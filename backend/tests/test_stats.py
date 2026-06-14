# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Tests for stats API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_top_rated(client: AsyncClient, user_token: str) -> None:
    """Test getting top-rated players."""
    response = await client.get(
        "/api/stats/top-rated",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "rating" in data[0]


@pytest.mark.asyncio
async def test_top_rated_with_limit(client: AsyncClient, user_token: str) -> None:
    """Test top-rated with custom limit."""
    response = await client.get(
        "/api/stats/top-rated?limit=5",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) <= 5


@pytest.mark.asyncio
async def test_overall_stats(client: AsyncClient, user_token: str) -> None:
    """Test getting overall stats for a player."""
    response = await client.get(
        "/api/stats/overall/1",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_games" in data
    assert "wins" in data
    assert "losses" in data
    assert "draws" in data


@pytest.mark.asyncio
async def test_head_to_head(client: AsyncClient, user_token: str) -> None:
    """Test head-to-head stats."""
    response = await client.get(
        "/api/stats/head-to-head/1/2",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "player1_id" in data
    assert "player2_id" in data
    assert "total_games" in data


@pytest.mark.asyncio
async def test_head_to_head_nonexistent(client: AsyncClient, user_token: str) -> None:
    """Test head-to-head with nonexistent player returns 0 games."""
    response = await client.get(
        "/api/stats/head-to-head/999999/999998",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    assert response.json()["total_games"] == 0


@pytest.mark.asyncio
async def test_overall_stats_empty_player(client: AsyncClient, user_token: str) -> None:
    """Test overall stats for player with no games."""
    response = await client.get(
        "/api/stats/overall/999999",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_games"] == 0
    assert data["wins"] == 0
    assert data["losses"] == 0
    assert data["draws"] == 0
