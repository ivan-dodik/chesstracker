"""Integration tests for full authentication flow."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_then_me_returns_user_data(client: AsyncClient):
    """Test full cycle: login → get token → GET /me → correct user data."""
    from app.core.security import hash_password
    from app.models import User
    from tests.conftest import TestSessionLocal

    async with TestSessionLocal() as session:
        user = User(username="flowuser", hashed_password=hash_password("flowpass"), role="user")
        session.add(user)
        await session.commit()

    # Login
    login_resp = await client.post("/api/auth/login", json={"username": "flowuser", "password": "flowpass"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # GET /me with token
    me_resp = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    data = me_resp.json()
    assert data["username"] == "flowuser"
    assert data["role"] == "user"


@pytest.mark.asyncio
async def test_authenticated_user_can_access_protected_endpoints(client: AsyncClient):
    """Test authenticated user can access protected endpoints (e.g., favorites)."""
    from app.core.security import hash_password
    from app.models import User
    from tests.conftest import TestSessionLocal

    async with TestSessionLocal() as session:
        user = User(username="someuser", hashed_password=hash_password("somepass"), role="user")
        session.add(user)
        await session.commit()

    # Login
    login_resp = await client.post("/api/auth/login", json={"username": "someuser", "password": "somepass"})
    token = login_resp.json()["access_token"]

    # Access protected endpoint
    resp = await client.get("/api/favorites", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_unauthenticated_user_cannot_access_protected_endpoints(client: AsyncClient):
    """Test unauthenticated user gets 401 on protected endpoints."""
    resp = await client.get("/api/favorites")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_register_as_admin_creates_user(client: AsyncClient, admin_token: str):
    """Test admin can register a new user via POST /api/auth/register."""
    response = await client.post(
        "/api/auth/register",
        json={"username": "newbyadmin", "password": "newpass123", "role": "user"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newbyadmin"
    assert data["role"] == "user"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_username_returns_400(client: AsyncClient, admin_token: str):
    """Test registering with an existing username returns 400."""
    from app.core.security import hash_password
    from app.models import User
    from tests.conftest import TestSessionLocal

    async with TestSessionLocal() as session:
        user = User(username="existinguser", hashed_password=hash_password("pass"), role="user")
        session.add(user)
        await session.commit()

    response = await client.post(
        "/api/auth/register",
        json={"username": "existinguser", "password": "newpass123", "role": "user"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 400
    assert "already taken" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_by_non_admin_returns_403(client: AsyncClient, user_token: str):
    """Test non-admin user gets 403 when trying to register new users."""
    response = await client.post(
        "/api/auth/register",
        json={"username": "anotheruser", "password": "pass123", "role": "user"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
