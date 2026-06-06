"""Tests for ratings API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_rating_history(client: AsyncClient, admin_token: str) -> None:
    """Test getting rating history for a player."""
    response = await client.get(
        "/api/players/1/rating-history",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_rating_history_with_dates(client: AsyncClient, admin_token: str) -> None:
    """Test rating history with date filter."""
    response = await client.get(
        "/api/players/1/rating-history?date_from=2020-01-01&date_to=2025-01-01",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_rating_history_no_auth(client: AsyncClient) -> None:
    """Test rating history without authentication (should work - public endpoint)."""
    response = await client.get("/api/players/1/rating-history")
    assert response.status_code == 200
