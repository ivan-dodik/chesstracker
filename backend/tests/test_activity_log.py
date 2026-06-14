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
