"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login returns a token."""
    # Create user via direct DB
    from app.core.security import hash_password
    from app.models import User
    from tests.conftest import TestSessionLocal

    async with TestSessionLocal() as session:
        user = User(username="testuser", hashed_password=hash_password("testpass"), role="user")
        session.add(user)
        await session.commit()

    response = await client.post("/api/auth/login", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    """Test login with wrong password returns 401."""
    from app.core.security import hash_password
    from app.models import User
    from tests.conftest import TestSessionLocal

    async with TestSessionLocal() as session:
        user = User(username="testuser", hashed_password=hash_password("testpass"), role="user")
        session.add(user)
        await session.commit()

    response = await client.post("/api/auth/login", json={"username": "testuser", "password": "wrongpass"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent username returns 401."""
    response = await client.post("/api/auth/login", json={"username": "nonexistent", "password": "somepass"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_endpoint(client: AsyncClient, admin_token: str):
    """Test GET /me returns current user."""
    response = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["role"] == "admin"


@pytest.mark.asyncio
async def test_me_unauthorized(client: AsyncClient):
    """Test GET /me without token returns 401."""
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_invalid_token(client: AsyncClient):
    """Test GET /me with invalid token returns 401."""
    response = await client.get("/api/auth/me", headers={"Authorization": "Bearer invalid_token_here"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_without_token_returns_401(client: AsyncClient):
    """Test POST /register without auth token returns 401."""
    response = await client.post(
        "/api/auth/register",
        json={"username": "newuser", "password": "newpass", "role": "user"},
    )
    assert response.status_code == 401
