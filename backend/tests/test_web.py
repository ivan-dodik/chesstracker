# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Tests for web page rendering (Jinja2 templates via web routes)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_index_with_token_returns_200(client: AsyncClient, admin_token: str):
    """Test GET / returns 200 and contains dashboard heading (with auth)."""
    response = await client.get(
        "/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert "Дашборд" in response.text


@pytest.mark.asyncio
async def test_index_with_cookie_returns_200(client: AsyncClient, admin_token: str):
    """Test GET / returns 200 with cookie auth."""
    response = await client.get(
        "/",
        cookies={"jwt_token": admin_token},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_index_contains_htmx_attributes(client: AsyncClient, admin_token: str):
    """Test dashboard page contains HTMX load triggers."""
    response = await client.get(
        "/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    # Top-rated section
    assert 'hx-get="/api/stats/top-rated"' in response.text
    # Favorites section
    assert 'hx-get="/api/favorites"' in response.text
    # Active tournaments
    assert 'hx-get="/api/tournaments?status=active&per_page=5"' in response.text
    # Recent results
    assert 'hx-get="/api/tournaments?per_page=1&status=completed"' in response.text


@pytest.mark.asyncio
async def test_index_contains_alpine_components(client: AsyncClient, admin_token: str):
    """Test dashboard page contains Alpine.js x-data attributes."""
    response = await client.get(
        "/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert 'x-data="ratingChart()"' in response.text
    assert 'x-data="overallStatsChart()"' in response.text
    assert 'x-data="authState()"' in response.text


@pytest.mark.asyncio
async def test_index_favorites_section_hidden_for_unauthenticated(client: AsyncClient, admin_token: str):
    """Test favorites section has x-show bound to auth state (BUGS.md fix)."""
    response = await client.get(
        "/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    # The favorites section should use x-show="isAuth" to hide for unauthenticated users
    assert 'x-data="{ isAuth: Auth.isAuthenticated() }"' in response.text
    assert 'x-show="isAuth"' in response.text


@pytest.mark.asyncio
async def test_index_without_token_redirects_to_login(client: AsyncClient):
    """Test GET / without auth redirects to /login."""
    response = await client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers.get("location") == "/login"


@pytest.mark.asyncio
async def test_players_page_with_token(client: AsyncClient, admin_token: str):
    """Test GET /players returns 200 with auth."""
    response = await client.get(
        "/players",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert "Игроки" in response.text


@pytest.mark.asyncio
async def test_players_page_without_token_redirects_to_login(client: AsyncClient):
    """Test GET /players without auth redirects to /login."""
    response = await client.get("/players", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers.get("location") == "/login"


@pytest.mark.asyncio
async def test_player_detail_page_with_token(client: AsyncClient, admin_token: str):
    """Test GET /players/1 returns 200 with auth."""
    response = await client.get(
        "/players/1",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert "Игрок" in response.text


@pytest.mark.asyncio
async def test_tournaments_page_with_token(client: AsyncClient, admin_token: str):
    """Test GET /tournaments returns 200 with auth."""
    response = await client.get(
        "/tournaments",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert "Турниры" in response.text


@pytest.mark.asyncio
async def test_tournament_detail_page_with_token(client: AsyncClient, admin_token: str):
    """Test GET /tournaments/1 returns 200 with auth."""
    response = await client.get(
        "/tournaments/1",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert "Турнир" in response.text


@pytest.mark.asyncio
async def test_login_page_returns_200(client: AsyncClient):
    """Test GET /login returns 200 and contains login form (public)."""
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


# --- CRUD Forms: Players ---


@pytest.mark.asyncio
async def test_player_create_page_admin(client: AsyncClient, admin_token: str):
    """Test GET /players/create returns 200 for admin."""
    response = await client.get(
        "/players/create",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert "Добавить игрока" in response.text
    assert 'x-data="playerCreateForm()"' in response.text


@pytest.mark.asyncio
async def test_player_create_page_non_admin_redirects(client: AsyncClient, user_token: str):
    """Test GET /players/create redirects non-admin to /players."""
    response = await client.get(
        "/players/create",
        headers={"Authorization": f"Bearer {user_token}"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers.get("location") == "/players"


@pytest.mark.asyncio
async def test_player_edit_page_admin(client: AsyncClient, admin_token: str):
    """Test GET /players/1/edit returns 200 for admin."""
    response = await client.get(
        "/players/1/edit",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert "Редактировать игрока" in response.text
    assert 'playerEditForm' in response.text


@pytest.mark.asyncio
async def test_player_edit_page_non_admin_redirects(client: AsyncClient, user_token: str):
    """Test GET /players/1/edit redirects non-admin."""
    response = await client.get(
        "/players/1/edit",
        headers={"Authorization": f"Bearer {user_token}"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers.get("location") == "/players"


# --- CRUD Forms: Tournaments ---


@pytest.mark.asyncio
async def test_tournament_create_page_admin(client: AsyncClient, admin_token: str):
    """Test GET /tournaments/create returns 200 for admin."""
    response = await client.get(
        "/tournaments/create",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert "Создать турнир" in response.text
    assert 'tournamentCreateForm' in response.text


@pytest.mark.asyncio
async def test_tournament_create_page_non_admin_redirects(client: AsyncClient, user_token: str):
    """Test GET /tournaments/create redirects non-admin."""
    response = await client.get(
        "/tournaments/create",
        headers={"Authorization": f"Bearer {user_token}"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers.get("location") == "/tournaments"


@pytest.mark.asyncio
async def test_tournament_edit_page_admin(client: AsyncClient, admin_token: str):
    """Test GET /tournaments/1/edit returns 200 for admin."""
    response = await client.get(
        "/tournaments/1/edit",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert "Редактировать турнир" in response.text
    assert 'tournamentEditForm' in response.text


@pytest.mark.asyncio
async def test_tournament_edit_page_non_admin_redirects(client: AsyncClient, user_token: str):
    """Test GET /tournaments/1/edit redirects non-admin."""
    response = await client.get(
        "/tournaments/1/edit",
        headers={"Authorization": f"Bearer {user_token}"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers.get("location") == "/tournaments"


# --- CRUD Forms: Games ---


@pytest.mark.asyncio
async def test_game_create_page_admin(client: AsyncClient, admin_token: str):
    """Test GET /tournaments/1/games/create returns 200 for admin."""
    response = await client.get(
        "/tournaments/1/games/create",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert "Добавить партию" in response.text
    assert 'gameCreateForm' in response.text


@pytest.mark.asyncio
async def test_game_create_page_non_admin_redirects(client: AsyncClient, user_token: str):
    """Test GET /tournaments/1/games/create redirects non-admin."""
    response = await client.get(
        "/tournaments/1/games/create",
        headers={"Authorization": f"Bearer {user_token}"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "/tournaments/1" in response.headers.get("location", "")


@pytest.mark.asyncio
async def test_game_edit_page_admin(client: AsyncClient, admin_token: str):
    """Test GET /games/1/edit returns 200 for admin."""
    response = await client.get(
        "/games/1/edit",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert "Редактировать партию" in response.text
    assert 'gameEditForm' in response.text


@pytest.mark.asyncio
async def test_game_edit_page_non_admin_redirects(client: AsyncClient, user_token: str):
    """Test GET /games/1/edit redirects non-admin."""
    response = await client.get(
        "/games/1/edit",
        headers={"Authorization": f"Bearer {user_token}"},
        follow_redirects=False,
    )
    assert response.status_code == 303
