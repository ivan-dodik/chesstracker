# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Tests for CSV import API endpoint."""

import pytest
from httpx import AsyncClient


def _make_csv_file(content: str, filename: str = "test.csv") -> dict:
    """Helper to create a multipart file dict for httpx."""
    return {
        "file": (filename, content.encode("utf-8"), "text/csv"),
    }


@pytest.mark.asyncio
async def test_import_csv_success(client: AsyncClient, admin_token: str):
    """Test admin can import CSV with results."""
    # Create tournament with players
    tourn = await client.post(
        "/api/tournaments",
        json={
            "name": "Import Tourn",
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

    await client.post(
        "/api/players", json={"name": "Alice", "rating": 2500, "city": "City"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    await client.post(
        "/api/players", json={"name": "Bob", "rating": 2400, "city": "City"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    csv_content = "player,round,opponent,result\nAlice,1,Bob,1-0\nBob,1,Alice,0-1\n"
    files = _make_csv_file(csv_content)

    response = await client.post(
        f"/api/tournaments/{tourn_id}/import/csv",
        files=files,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_import_csv_unauthorized(client: AsyncClient):
    """Test import CSV without auth returns 401."""
    csv_content = "player,round,opponent,result\nAlice,1,Bob,1-0\n"
    files = _make_csv_file(csv_content)

    response = await client.post(
        "/api/tournaments/1/import/csv",
        files=files,
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_import_csv_invalid_format(client: AsyncClient, admin_token: str):
    """Test import of non-CSV file returns 400."""
    files = {
        "file": ("data.txt", b"not a csv", "text/plain"),
    }
    response = await client.post(
        "/api/tournaments/1/import/csv",
        files=files,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_import_csv_missing_file(client: AsyncClient, admin_token: str):
    """Test import without file returns 422."""
    response = await client.post(
        "/api/tournaments/1/import/csv",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 422
