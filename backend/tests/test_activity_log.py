# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Tests for activity log API endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_activity_log_admin(client: AsyncClient, admin_token: str):
    """Test admin can get activity log."""
    response = await client.get(
        "/api/activity-log?per_page=10",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_activity_log_forbidden(client: AsyncClient, user_token: str):
    """Test regular user cannot get activity log (403)."""
    response = await client.get(
        "/api/activity-log",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_activity_log_unauthorized(client: AsyncClient):
    """Test unauthenticated user cannot get activity log (401)."""
    response = await client.get("/api/activity-log")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_activity_log_pagination(client: AsyncClient, admin_token: str):
    """Test activity log returns paginated results."""
    response = await client.get(
        "/api/activity-log?per_page=5&page=1",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 5


@pytest.mark.asyncio
async def test_activity_log_player_create(client: AsyncClient, admin_token: str):
    """Test that player creation is logged with user_id."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create a player
    resp = await client.post(
        "/api/players",
        json={"name": "LogTest Player", "rating": 1500},
        headers=headers,
    )
    assert resp.status_code == 201
    player_id = resp.json()["id"]

    # Check activity log
    resp = await client.get(
        "/api/activity-log?entity_type=player&action=create",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1

    # Find the log entry for this player
    entry = next((e for e in data["items"] if e["entity_id"] == player_id), None)
    assert entry is not None
    assert entry["user_id"] is not None
    assert entry["action"] == "create"
    assert entry["entity_type"] == "player"
    assert entry["new_values"] is not None
    assert entry["new_values"]["name"] == "LogTest Player"


@pytest.mark.asyncio
async def test_activity_log_player_update(client: AsyncClient, admin_token: str):
    """Test that player update logs old_values and new_values."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create a player
    resp = await client.post(
        "/api/players",
        json={"name": "UpdateTest", "rating": 1400},
        headers=headers,
    )
    player_id = resp.json()["id"]

    # Update the player
    resp = await client.put(
        f"/api/players/{player_id}",
        json={"name": "UpdateTest Renamed", "rating": 1500},
        headers=headers,
    )
    assert resp.status_code == 200

    # Check activity log for update
    resp = await client.get(
        "/api/activity-log?entity_type=player&action=update",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    entry = next((e for e in data["items"] if e["entity_id"] == player_id), None)
    assert entry is not None
    assert entry["old_values"] is not None
    assert entry["new_values"] is not None
    assert entry["old_values"]["name"] == "UpdateTest"
    assert entry["new_values"]["name"] == "UpdateTest Renamed"


@pytest.mark.asyncio
async def test_activity_log_game_create_with_user_id(client: AsyncClient, admin_token: str):
    """Test that game creation logs user_id correctly."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create tournament
    resp = await client.post(
        "/api/tournaments",
        json={"name": "LogTour", "start_date": "2026-01-01", "end_date": "2026-01-02"},
        headers=headers,
    )
    tournament_id = resp.json()["id"]

    # Create two players
    resp1 = await client.post("/api/players", json={"name": "White Player", "rating": 1500}, headers=headers)
    resp2 = await client.post("/api/players", json={"name": "Black Player", "rating": 1500}, headers=headers)
    white_id = resp1.json()["id"]
    black_id = resp2.json()["id"]

    # Create game
    resp = await client.post(
        f"/api/tournaments/{tournament_id}/games",
        json={
            "white_player_id": white_id,
            "black_player_id": black_id,
            "game_round": 1,
            "result": "1-0",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    game_id = resp.json()["id"]

    # Check game creation log
    resp = await client.get(
        "/api/activity-log?entity_type=game&action=create",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    entry = next((e for e in data["items"] if e["entity_id"] == game_id), None)
    assert entry is not None
    assert entry["user_id"] is not None
    assert entry["new_values"]["result"] == "1-0"


@pytest.mark.asyncio
async def test_activity_log_rating_update_with_user_id(client: AsyncClient, admin_token: str):
    """Test that rating updates include user_id from the game creator."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create tournament
    resp = await client.post(
        "/api/tournaments",
        json={"name": "RatingTour", "start_date": "2026-02-01", "end_date": "2026-02-02"},
        headers=headers,
    )
    tournament_id = resp.json()["id"]

    # Create two players with known ratings
    resp1 = await client.post("/api/players", json={"name": "Rating W", "rating": 1500}, headers=headers)
    resp2 = await client.post("/api/players", json={"name": "Rating B", "rating": 1500}, headers=headers)
    white_id = resp1.json()["id"]
    black_id = resp2.json()["id"]

    # Create game with result → triggers rating update
    resp = await client.post(
        f"/api/tournaments/{tournament_id}/games",
        json={
            "white_player_id": white_id,
            "black_player_id": black_id,
            "game_round": 1,
            "result": "1-0",
        },
        headers=headers,
    )
    assert resp.status_code == 201

    # Check rating update logs
    resp = await client.get(
        "/api/activity-log?entity_type=rating&action=update",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    # Rating logs should have user_id (not None) after the fix
    for entry in data["items"]:
        assert entry["user_id"] is not None
        assert entry["old_values"] is not None
        assert entry["new_values"] is not None
        assert "rating" in entry["old_values"]
        assert "rating" in entry["new_values"]
        assert "change" in entry["new_values"]


@pytest.mark.asyncio
async def test_activity_log_import(client: AsyncClient, admin_token: str):
    """Test that CSV import creates activity log entries."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create tournament
    resp = await client.post(
        "/api/tournaments",
        json={"name": "ImportTour", "start_date": "2026-03-01", "end_date": "2026-03-02"},
        headers=headers,
    )
    tournament_id = resp.json()["id"]

    # Create players
    resp1 = await client.post("/api/players", json={"name": "ImportWhite", "rating": 1500}, headers=headers)
    resp2 = await client.post("/api/players", json={"name": "ImportBlack", "rating": 1500}, headers=headers)
    assert resp1.status_code == 201
    assert resp2.status_code == 201

    # Import CSV via multipart file upload
    csv_content = "round,white_player,black_player,result\n1,ImportWhite,ImportBlack,1-0\n"
    resp = await client.post(
        f"/api/tournaments/{tournament_id}/import/csv",
        files={"file": ("test.csv", csv_content.encode("utf-8"), "text/csv")},
        headers=headers,
    )
    assert resp.status_code == 200
    import_data = resp.json()
    assert import_data["games_created"] >= 1

    # Check activity log for import
    resp = await client.get(
        "/api/activity-log?entity_type=import",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    entry = data["items"][0]
    assert entry["action"] == "import"
    assert entry["user_id"] is not None
    assert entry["new_values"]["games_created"] >= 1


@pytest.mark.asyncio
async def test_activity_log_favorite_add_remove(client: AsyncClient, admin_token: str):
    """Test that favorite add/remove are logged."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create a player
    resp = await client.post("/api/players", json={"name": "FavPlayer", "rating": 1500}, headers=headers)
    player_id = resp.json()["id"]

    # Add to favorites
    resp = await client.post(
        f"/api/favorites/{player_id}",
        headers=headers,
    )
    assert resp.status_code == 201

    # Check activity log for favorite create
    resp = await client.get(
        "/api/activity-log?entity_type=favorite&action=create",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    entry = data["items"][0]
    assert entry["user_id"] is not None
    assert entry["new_values"]["player_id"] == player_id

    # Remove from favorites
    resp = await client.delete(
        f"/api/favorites/{player_id}",
        headers=headers,
    )
    assert resp.status_code == 204

    # Check activity log for favorite delete
    resp = await client.get(
        "/api/activity-log?entity_type=favorite&action=delete",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    entry = data["items"][0]
    assert entry["old_values"]["player_id"] == player_id


@pytest.mark.asyncio
async def test_activity_log_filter_by_entity_type(client: AsyncClient, admin_token: str):
    """Test filtering activity log by entity_type."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Create a player (generates player log)
    resp = await client.post("/api/players", json={"name": "FilterPlayer", "rating": 1500}, headers=headers)
    assert resp.status_code == 201

    # Filter by player
    resp = await client.get("/api/activity-log?entity_type=player", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    for item in data["items"]:
        assert item["entity_type"] == "player"

    # Filter by nonexistent type → should return empty
    resp = await client.get("/api/activity-log?entity_type=nonexistent", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


@pytest.mark.asyncio
async def test_activity_log_timestamp(client: AsyncClient, admin_token: str):
    """Test that activity log entries have valid timestamps."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp = await client.post("/api/players", json={"name": "TimestampPlayer", "rating": 1500}, headers=headers)
    assert resp.status_code == 201

    resp = await client.get("/api/activity-log?per_page=1", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) >= 1
    entry = data["items"][0]
    assert entry["timestamp"] is not None
    # Timestamp should be a valid ISO format string
    from datetime import datetime
    datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
