"""Tests for stats API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_top_rated(client: AsyncClient) -> None:
    """Test getting top-rated players."""
    response = await client.get("/api/stats/top-rated")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "rating" in data[0]


@pytest.mark.asyncio
async def test_top_rated_with_limit(client: AsyncClient) -> None:
    """Test top-rated with custom limit."""
    response = await client.get("/api/stats/top-rated?limit=5")
    assert response.status_code == 200
    assert len(response.json()) <= 5


@pytest.mark.asyncio
async def test_overall_stats(client: AsyncClient) -> None:
    """Test getting overall stats for a player."""
    response = await client.get("/api/stats/overall/1")
    assert response.status_code == 200
    data = response.json()
    assert "total_games" in data
    assert "wins" in data
    assert "losses" in data
    assert "draws" in data


@pytest.mark.asyncio
async def test_head_to_head(client: AsyncClient) -> None:
    """Test head-to-head stats."""
    response = await client.get("/api/stats/head-to-head/1/2")
    assert response.status_code == 200
    data = response.json()
    assert "player1_id" in data
    assert "player2_id" in data
    assert "total_games" in data