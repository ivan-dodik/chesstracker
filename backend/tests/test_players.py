# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Tests for players API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_players(client: AsyncClient, user_token: str):
    """Test GET /api/players returns paginated list."""
    from app.models import Player
    from tests.conftest import TestSessionLocal

    # Create test players
    async with TestSessionLocal() as session:
        session.add_all([
            Player(name="Test Player 1", rating=2500, city="Moscow"),
            Player(name="Test Player 2", rating=2400, city="SPB"),
        ])
        await session.commit()

    response = await client.get(
        "/api/players?per_page=10",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_players_unauthorized(client: AsyncClient):
    """Test GET /api/players without token returns 401."""
    response = await client.get("/api/players?per_page=10")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_player_admin(client: AsyncClient, admin_token: str):
    """Test admin can create a player."""
    response = await client.post(
        "/api/players",
        json={"name": "New Player", "rating": 2000, "city": "Kazan"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Player"
    assert data["rating"] == 2000


@pytest.mark.asyncio
async def test_create_player_forbidden(client: AsyncClient, user_token: str):
    """Test regular user cannot create a player."""
    response = await client.post(
        "/api/players",
        json={"name": "New Player", "rating": 2000},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_player_by_id(client: AsyncClient, admin_token: str, user_token: str):
    """Test GET /api/players/{id} returns player details."""
    from app.models import Player
    from tests.conftest import TestSessionLocal

    async with TestSessionLocal() as session:
        player = Player(name="Detail Player", rating=2600, city="Novosibirsk")
        session.add(player)
        await session.commit()
        player_id = player.id

    response = await client.get(
        f"/api/players/{player_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Detail Player"


@pytest.mark.asyncio
async def test_get_player_by_id_unauthorized(client: AsyncClient):
    """Test GET /api/players/{id} without token returns 401."""
    response = await client.get("/api/players/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_player_not_found(client: AsyncClient, user_token: str):
    """Test GET /api/players/{id} for nonexistent player returns 404."""
    response = await client.get(
        "/api/players/999999",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_player_admin(client: AsyncClient, admin_token: str):
    """Test admin can update a player."""
    # Create player
    create_resp = await client.post(
        "/api/players",
        json={"name": "Old Name", "rating": 2000, "city": "City"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert create_resp.status_code == 201
    player_id = create_resp.json()["id"]

    # Update
    response = await client.put(
        f"/api/players/{player_id}",
        json={"name": "Updated Name", "rating": 2500, "city": "New City"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["rating"] == 2500


@pytest.mark.asyncio
async def test_delete_player_admin(client: AsyncClient, admin_token: str, user_token: str):
    """Test admin can delete a player."""
    # Create player
    create_resp = await client.post(
        "/api/players",
        json={"name": "To Delete", "rating": 1800, "city": "City"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert create_resp.status_code == 201
    player_id = create_resp.json()["id"]

    # Delete
    response = await client.delete(
        f"/api/players/{player_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 204

    # Verify deleted
    get_resp = await client.get(
        f"/api/players/{player_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_update_player_not_found(client: AsyncClient, admin_token: str):
    """Test updating nonexistent player returns 404."""
    response = await client.put(
        "/api/players/999999",
        json={"name": "Ghost", "rating": 1000, "city": "Nowhere"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_player_not_found(client: AsyncClient, admin_token: str):
    """Test deleting nonexistent player returns 404."""
    response = await client.delete(
        "/api/players/999999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
