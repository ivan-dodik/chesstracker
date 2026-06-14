# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

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


# ============================================================
# Tests for get_current_user_for_web (cookie-based auth)
# ============================================================

@pytest.mark.asyncio
async def test_web_auth_with_bearer_token(client: AsyncClient, admin_token: str):
    """Test web page can be accessed with Authorization header (HTMX scenario)."""

    # We test via a web endpoint - but since they're not protected yet,
    # we test the dependency directly via app injection
    response = await client.get(
        "/players",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_web_auth_with_cookie(client: AsyncClient, admin_token: str):
    """Test web page can be accessed with jwt_token cookie (direct browser navigation)."""
    response = await client.get(
        "/players",
        cookies={"jwt_token": admin_token},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_web_auth_without_credentials_redirects_to_login(client: AsyncClient):
    """Test web page without any credentials redirects to /login."""
    response = await client.get("/players", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers.get("location") == "/login"


@pytest.mark.asyncio
async def test_web_auth_with_invalid_token_returns_401(client: AsyncClient):
    """Test web page with invalid token returns 401."""
    response = await client.get(
        "/players",
        headers={"Authorization": "Bearer invalid_token_here"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_web_auth_with_expired_token_returns_401(client: AsyncClient):
    """Test web page with expired/malformed token returns 401."""
    response = await client.get(
        "/players",
        cookies={"jwt_token": "expired.or.malformed.token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_page_public(client: AsyncClient):
    """Test login page is publicly accessible without auth."""
    response = await client.get("/login")
    assert response.status_code == 200
