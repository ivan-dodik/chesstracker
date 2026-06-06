"""Tests for players API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_players(client: AsyncClient, user_token: str):
    """Test GET /api/players returns paginated list."""
    from app.core.security import hash_password
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
async def test_get_player_by_id(client: AsyncClient, admin_token: str):
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
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Detail Player"