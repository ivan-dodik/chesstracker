"""Tests for web page rendering (Jinja2 templates via web routes)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_index_returns_200(client: AsyncClient):
    """Test GET / returns 200 and contains dashboard heading."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "Дашборд" in response.text


@pytest.mark.asyncio
async def test_index_contains_htmx_attributes(client: AsyncClient):
    """Test dashboard page contains HTMX load triggers."""
    response = await client.get("/")
    # Top-rated section
    assert 'hx-get="/api/stats/top-rated"' in response.text
    # Favorites section
    assert 'hx-get="/api/favorites"' in response.text
    # Active tournaments
    assert 'hx-get="/api/tournaments?status=active&per_page=5"' in response.text
    # Recent results
    assert 'hx-get="/api/tournaments?per_page=1&status=completed"' in response.text


@pytest.mark.asyncio
async def test_index_contains_alpine_components(client: AsyncClient):
    """Test dashboard page contains Alpine.js x-data attributes."""
    response = await client.get("/")
    assert 'x-data="ratingChart()"' in response.text
    assert 'x-data="overallStatsChart()"' in response.text
    assert 'x-data="authState()"' in response.text


@pytest.mark.asyncio
async def test_index_favorites_section_hidden_for_unauthenticated(client: AsyncClient):
    """Test favorites section has x-show bound to auth state (BUGS.md fix)."""
    response = await client.get("/")
    # The favorites section should use x-show="isAuth" to hide for unauthenticated users
    assert 'x-data="{ isAuth: Auth.isAuthenticated() }"' in response.text
    assert 'x-show="isAuth"' in response.text


@pytest.mark.asyncio
async def test_login_page_returns_200(client: AsyncClient):
    """Test GET /login returns 200 and contains login form."""
    response = await client.get("/login")
    assert response.status_code == 200
    assert "Вход в Chess Tracker" in response.text


@pytest.mark.asyncio
async def test_login_page_contains_form_elements(client: AsyncClient):
    """Test login page has username field, password field, and submit button."""
    response = await client.get("/login")
    assert 'id="username"' in response.text
    assert 'id="password"' in response.text
    assert "Войти" in response.text


@pytest.mark.asyncio
async def test_login_page_contains_alpine_form(client: AsyncClient):
    """Test login page has Alpine.js loginForm component."""
    response = await client.get("/login")
    assert 'x-data="loginForm()"' in response.text
    assert '@submit.prevent="submit()"' in response.text