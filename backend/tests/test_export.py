"""Tests for CSV export API endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_export_csv_success(client: AsyncClient, admin_token: str, user_token: str):
    """Test export tournament standings as CSV returns valid CSV."""
    # Create tournament with players and a game
    tourn = await client.post(
        "/api/tournaments",
        json={
            "name": "Export Tourn",
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

    await client.post(
        f"/api/tournaments/{tourn_id}/games",
        json={"game_round": 1, "white_player_id": p1_id, "black_player_id": p2_id, "result": "1-0"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Export
    response = await client.get(
        f"/api/tournaments/{tourn_id}/export/csv",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "Player" in response.text or "player" in response.text.lower()


@pytest.mark.asyncio
async def test_export_csv_nonexistent(client: AsyncClient, user_token: str):
    """Test export for nonexistent tournament returns 404."""
    response = await client.get(
        "/api/tournaments/999999/export/csv",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_export_csv_empty_tournament(client: AsyncClient, admin_token: str, user_token: str):
    """Test export for tournament with no games returns valid CSV."""
    tourn = await client.post(
        "/api/tournaments",
        json={
            "name": "Empty Tourn",
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

    response = await client.get(
        f"/api/tournaments/{tourn_id}/export/csv",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
