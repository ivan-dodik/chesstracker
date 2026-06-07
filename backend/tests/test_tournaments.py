"""Tests for tournaments API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_tournaments(client: AsyncClient, user_token: str):
    """Test GET /api/tournaments returns paginated list."""
    response = await client.get(
        "/api/tournaments?per_page=10",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_list_tournaments_empty(client: AsyncClient, user_token: str):
    """Test GET /api/tournaments returns empty list when no tournaments exist."""
    response = await client.get(
        "/api/tournaments?per_page=10",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_create_tournament_admin(client: AsyncClient, admin_token: str):
    """Test admin can create a tournament."""
    response = await client.post(
        "/api/tournaments",
        json={
            "name": "Test Tournament",
            "start_date": "2026-06-01",
            "end_date": "2026-06-10",
            "location": "Moscow",
            "rounds": 5,
            "type": "classic",
            "status": "active",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Tournament"
    assert data["location"] == "Moscow"


@pytest.mark.asyncio
async def test_create_tournament_forbidden(client: AsyncClient, user_token: str):
    """Test regular user cannot create a tournament."""
    response = await client.post(
        "/api/tournaments",
        json={
            "name": "Test Tournament",
            "start_date": "2026-06-01",
            "end_date": "2026-06-10",
            "rounds": 5,
            "type": "classic",
            "status": "active",
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_tournament_by_id(client: AsyncClient, admin_token: str, user_token: str):
    """Test GET /api/tournaments/{id} returns tournament details."""
    # First create a tournament
    create_resp = await client.post(
        "/api/tournaments",
        json={
            "name": "Detail Tournament",
            "start_date": "2026-06-01",
            "end_date": "2026-06-10",
            "location": "SPB",
            "rounds": 7,
            "type": "blitz",
            "status": "active",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert create_resp.status_code == 201
    tournament_id = create_resp.json()["id"]

    response = await client.get(
        f"/api/tournaments/{tournament_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Detail Tournament"
    assert data["location"] == "SPB"


@pytest.mark.asyncio
async def test_get_tournament_not_found(client: AsyncClient, user_token: str):
    """Test GET /api/tournaments/{id} with nonexistent ID returns 404."""
    response = await client.get(
        "/api/tournaments/999999",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_tournament_admin(client: AsyncClient, admin_token: str):
    """Test admin can update a tournament."""
    # Create tournament
    create_resp = await client.post(
        "/api/tournaments",
        json={
            "name": "Old Name",
            "start_date": "2026-06-01",
            "end_date": "2026-06-10",
            "location": "City",
            "rounds": 3,
            "type": "rapid",
            "status": "active",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert create_resp.status_code == 201
    tournament_id = create_resp.json()["id"]

    # Update
    response = await client.put(
        f"/api/tournaments/{tournament_id}",
        json={
            "name": "Updated Name",
            "start_date": "2026-06-01",
            "end_date": "2026-06-15",
            "location": "New City",
            "rounds": 5,
            "type": "classic",
            "status": "completed",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_delete_tournament_admin(client: AsyncClient, admin_token: str, user_token: str):
    """Test admin can delete a tournament."""
    # Create tournament
    create_resp = await client.post(
        "/api/tournaments",
        json={
            "name": "To Delete",
            "start_date": "2026-06-01",
            "end_date": "2026-06-10",
            "location": "City",
            "rounds": 3,
            "type": "classic",
            "status": "active",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert create_resp.status_code == 201
    tournament_id = create_resp.json()["id"]

    # Delete
    response = await client.delete(
        f"/api/tournaments/{tournament_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 204

    # Verify deleted
    get_resp = await client.get(
        f"/api/tournaments/{tournament_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_get_standings(client: AsyncClient, admin_token: str, user_token: str):
    """Test GET /api/tournaments/{id}/standings returns standings."""
    # Create a tournament with players and games
    create_resp = await client.post(
        "/api/tournaments",
        json={
            "name": "Standings Tournament",
            "start_date": "2026-06-01",
            "end_date": "2026-06-10",
            "location": "City",
            "rounds": 1,
            "type": "classic",
            "status": "active",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert create_resp.status_code == 201
    tournament_id = create_resp.json()["id"]

    # Create players
    p1 = await client.post(
        "/api/players",
        json={"name": "Player 1", "rating": 2500, "city": "City"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    p2 = await client.post(
        "/api/players",
        json={"name": "Player 2", "rating": 2400, "city": "City"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert p1.status_code == 201
    assert p2.status_code == 201
    p1_id = p1.json()["id"]
    p2_id = p2.json()["id"]

    # Create a game
    game = await client.post(
        f"/api/tournaments/{tournament_id}/games",
        json={
            "round": 1,
            "white_player_id": p1_id,
            "black_player_id": p2_id,
            "result": "1-0",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert game.status_code == 201

    # Get standings
    response = await client.get(
        f"/api/tournaments/{tournament_id}/standings",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
