"""Tests for games API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_games_by_tournament(client: AsyncClient, admin_token: str, user_token: str):
    """Test GET /api/tournaments/{id}/games returns games."""
    # Create tournament, players, and a game
    tourn = await client.post(
        "/api/tournaments",
        json={
            "name": "Games Tournament",
            "start_date": "2026-06-01",
            "end_date": "2026-06-10",
            "location": "City",
            "rounds": 1,
            "type": "classic",
            "status": "active",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert tourn.status_code == 201
    tourn_id = tourn.json()["id"]

    p1 = await client.post(
        "/api/players",
        json={"name": "White Player", "rating": 2500, "city": "City"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    p2 = await client.post(
        "/api/players",
        json={"name": "Black Player", "rating": 2400, "city": "City"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    p1_id = p1.json()["id"]
    p2_id = p2.json()["id"]

    game = await client.post(
        f"/api/tournaments/{tourn_id}/games",
        json={"game_round": 1, "white_player_id": p1_id, "black_player_id": p2_id, "result": "1-0"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert game.status_code == 201

    # List games
    response = await client.get(
        f"/api/tournaments/{tourn_id}/games?per_page=10",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1
    assert data["items"][0]["game_round"] == 1


@pytest.mark.asyncio
async def test_create_game_admin(client: AsyncClient, admin_token: str):
    """Test admin can create a game."""
    tourn = await client.post(
        "/api/tournaments",
        json={
            "name": "Create Game Tourn",
            "start_date": "2026-06-01",
            "end_date": "2026-06-10",
            "location": "City",
            "rounds": 1,
            "type": "classic",
            "status": "active",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    tourn_id = tourn.json()["id"]

    p1 = await client.post(
        "/api/players", json={"name": "P1", "rating": 2500, "city": "City"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    p2 = await client.post(
        "/api/players", json={"name": "P2", "rating": 2400, "city": "City"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    p1_id = p1.json()["id"]
    p2_id = p2.json()["id"]

    response = await client.post(
        f"/api/tournaments/{tourn_id}/games",
        json={"game_round": 1, "white_player_id": p1_id, "black_player_id": p2_id, "result": "1-0"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["game_round"] == 1
    assert data["result"] == "1-0"


@pytest.mark.asyncio
async def test_create_game_unauthorized(client: AsyncClient):
    """Test creating a game without auth returns 401."""
    response = await client.post(
        "/api/tournaments/1/games",
        json={"game_round": 1, "white_player_id": 1, "black_player_id": 2, "result": "1-0"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_game_result(client: AsyncClient, admin_token: str):
    """Test admin can update a game result."""
    # Setup
    tourn = await client.post(
        "/api/tournaments",
        json={
            "name": "Update Game Tourn",
            "start_date": "2026-06-01",
            "end_date": "2026-06-10",
            "location": "City",
            "rounds": 1,
            "type": "classic",
            "status": "active",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    tourn_id = tourn.json()["id"]

    p1 = await client.post(
        "/api/players", json={"name": "P1", "rating": 2500, "city": "City"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    p2 = await client.post(
        "/api/players", json={"name": "P2", "rating": 2400, "city": "City"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    p1_id = p1.json()["id"]
    p2_id = p2.json()["id"]

    game = await client.post(
        f"/api/tournaments/{tourn_id}/games",
        json={"game_round": 1, "white_player_id": p1_id, "black_player_id": p2_id, "result": "1-0"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    game_id = game.json()["id"]

    # Update result
    response = await client.put(
        f"/api/games/{game_id}",
        json={"result": "0-1"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["result"] == "0-1"


@pytest.mark.asyncio
async def test_delete_game_admin(client: AsyncClient, admin_token: str):
    """Test admin can delete a game."""
    tourn = await client.post(
        "/api/tournaments",
        json={
            "name": "Delete Game Tourn",
            "start_date": "2026-06-01",
            "end_date": "2026-06-10",
            "location": "City",
            "rounds": 1,
            "type": "classic",
            "status": "active",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    tourn_id = tourn.json()["id"]

    p1 = await client.post(
        "/api/players", json={"name": "P1", "rating": 2500, "city": "City"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    p2 = await client.post(
        "/api/players", json={"name": "P2", "rating": 2400, "city": "City"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    p1_id = p1.json()["id"]
    p2_id = p2.json()["id"]

    game = await client.post(
        f"/api/tournaments/{tourn_id}/games",
        json={"game_round": 1, "white_player_id": p1_id, "black_player_id": p2_id, "result": "½-½"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    game_id = game.json()["id"]

    response = await client.delete(
        f"/api/games/{game_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_list_games_nonexistent_tournament(client: AsyncClient, user_token: str):
    """Test GET games for nonexistent tournament returns empty list."""
    response = await client.get(
        "/api/tournaments/999999/games",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []
