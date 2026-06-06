"""Tests for favorites API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_favorites(client: AsyncClient, user_token: str) -> None:
    """Test getting favorites for authenticated user."""
    response = await client.get(
        "/api/favorites",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_favorites_unauthorized(client: AsyncClient) -> None:
    """Test getting favorites without auth (should fail)."""
    response = await client.get("/api/favorites")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_add_and_remove_favorite(client: AsyncClient, user_token: str, admin_token: str) -> None:
    """Test adding and removing a player from favorites."""
    # First create a player (admin only)
    player_resp = await client.post(
        "/api/players",
        json={"name": "Test Player", "rating": 1500, "city": "Test City"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert player_resp.status_code == 201
    player_id = player_resp.json()["id"]

    # Add to favorites
    response = await client.post(
        f"/api/favorites/{player_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 201

    # Verify in list
    response = await client.get(
        "/api/favorites",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["player_id"] == player_id

    # Remove
    response = await client.delete(
        f"/api/favorites/{player_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 204

    # Verify removed
    response = await client.get(
        "/api/favorites",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_add_favorite_duplicate(client: AsyncClient, user_token: str, admin_token: str) -> None:
    """Test adding duplicate favorite (should return 409)."""
    # Create a player
    player_resp = await client.post(
        "/api/players",
        json={"name": "Test Player 2", "rating": 1600, "city": "City"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert player_resp.status_code == 201
    player_id = player_resp.json()["id"]

    response = await client.post(
        f"/api/favorites/{player_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 201

    response = await client.post(
        f"/api/favorites/{player_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_delete_nonexistent_favorite(client: AsyncClient, user_token: str) -> None:
    """Test removing a non-existent favorite (should fail with 404)."""
    response = await client.delete(
        "/api/favorites/999999",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404
