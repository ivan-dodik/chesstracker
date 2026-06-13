"""V2: CRUD верификация — поиск, фильтрация, пагинация, валидация.

Проверяет функциональные требования из project_task.md:
- Поиск и фильтрация: турниров по дате, местоположению, статусу; игроков по имени, рейтингу, городу
- Пагинация списков
- Валидация на сервере (CRUD с валидацией)
"""

import pytest
from httpx import AsyncClient


class TestPlayersSearchFilterPagination:
    """Поиск и фильтрация игроков."""

    @pytest.mark.asyncio
    async def test_player_search_by_name(self, client: AsyncClient, admin_token: str):
        """Поиск игрока по имени (частичное совпадение)."""
        # Создаём нескольких игроков
        for name in ["Alice Wonder", "Bob Builder", "Charlie Chaplin"]:
            resp = await client.post(
                "/api/players",
                json={"name": name, "rating": 2000, "city": "Moscow"},
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 201

        # Поиск по "Alice"
        resp = await client.get(
            "/api/players?name=Alice",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        names = [item["name"] for item in data["items"]]
        assert any("Alice" in n for n in names)

    @pytest.mark.asyncio
    async def test_player_filter_by_rating_range(self, client: AsyncClient, admin_token: str):
        """Фильтрация игроков по диапазону рейтинга."""
        ratings = [1500, 2000, 2500]
        for r in ratings:
            resp = await client.post(
                "/api/players",
                json={"name": f"Player {r}", "rating": r, "city": "City"},
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 201

        resp = await client.get(
            "/api/players?rating_min=1800&rating_max=2200",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        for item in data["items"]:
            assert 1800 <= item["rating"] <= 2200

    @pytest.mark.asyncio
    async def test_player_filter_by_city(self, client: AsyncClient, admin_token: str):
        """Фильтрация игроков по городу."""
        resp = await client.post(
            "/api/players",
            json={"name": "City Player", "rating": 2000, "city": "Vladivostok"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 201

        resp = await client.get(
            "/api/players?city=Vladivostok",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        for item in data["items"]:
            assert "Vladivostok" in item["city"]

    @pytest.mark.asyncio
    async def test_player_pagination(self, client: AsyncClient, admin_token: str):
        """Пагинация списка игроков."""
        # Создаём минимум 3 игроков
        for i in range(3):
            resp = await client.post(
                "/api/players",
                json={"name": f"Pagination Player {i}", "rating": 2000 + i, "city": "City"},
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 201

        # Страница 1, 2 элемента
        resp = await client.get(
            "/api/players?page=1&per_page=2",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) <= 2
        assert data["page"] == 1
        assert data["per_page"] == 2
        assert data["total"] >= 3


class TestTournamentsSearchFilterPagination:
    """Поиск и фильтрация турниров."""

    @pytest.mark.asyncio
    async def test_tournament_filter_by_status(self, client: AsyncClient, admin_token: str):
        """Фильтрация турниров по статусу."""
        # Создаём завершённый турнир
        resp = await client.post(
            "/api/tournaments",
            json={
                "name": "Completed Tourney",
                "start_date": "2026-01-01",
                "end_date": "2026-01-10",
                "location": "Moscow",
                "rounds": 5,
                "type": "classic",
                "status": "completed",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 201

        # Фильтр по статусу
        resp = await client.get(
            "/api/tournaments?status=completed",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        for item in data["items"]:
            assert item["status"] == "completed"

    @pytest.mark.asyncio
    async def test_tournament_filter_by_location(self, client: AsyncClient, admin_token: str):
        """Фильтрация турниров по местоположению."""
        resp = await client.post(
            "/api/tournaments",
            json={
                "name": "Siberian Open",
                "start_date": "2026-02-01",
                "end_date": "2026-02-10",
                "location": "Novosibirsk",
                "rounds": 7,
                "type": "blitz",
                "status": "active",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 201

        resp = await client.get(
            "/api/tournaments?location=Novosibirsk",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        for item in data["items"]:
            assert "Novosibirsk" in item["location"]

    @pytest.mark.asyncio
    async def test_tournament_pagination(self, client: AsyncClient, admin_token: str):
        """Пагинация списка турниров."""
        for i in range(3):
            resp = await client.post(
                "/api/tournaments",
                json={
                    "name": f"Paginated Tourney {i}",
                    "start_date": f"2026-03-{1+i:02d}",
                    "end_date": f"2026-03-{8+i:02d}",
                    "location": "City",
                    "rounds": 3,
                    "type": "rapid",
                    "status": "active",
                },
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 201

        resp = await client.get(
            "/api/tournaments?page=1&per_page=2",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) <= 2
        assert data["page"] == 1
        assert data["per_page"] == 2


class TestCRUDValidation:
    """Валидация CRUD операций."""

    @pytest.mark.asyncio
    async def test_create_player_invalid_rating_negative(self, client: AsyncClient, admin_token: str):
        """Создание игрока с отрицательным рейтингом → 422."""
        resp = await client.post(
            "/api/players",
            json={"name": "Bad Player", "rating": -100, "city": "City"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_player_missing_name(self, client: AsyncClient, admin_token: str):
        """Создание игрока без имени → 422."""
        resp = await client.post(
            "/api/players",
            json={"rating": 2000, "city": "City"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_tournament_invalid_dates(self, client: AsyncClient, admin_token: str):
        """Создание турнира с end_date раньше start_date."""
        resp = await client.post(
            "/api/tournaments",
            json={
                "name": "Bad Dates",
                "start_date": "2026-06-10",
                "end_date": "2026-06-01",
                "location": "City",
                "rounds": 5,
                "type": "classic",
                "status": "active",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        # Валидация дат может быть на уровне схемы или сервиса
        # Допустимы оба варианта: 422 (схема) или 400 (бизнес-логика)
        assert resp.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_create_tournament_invalid_type(self, client: AsyncClient, admin_token: str):
        """Создание турнира с недопустимым типом → 422."""
        resp = await client.post(
            "/api/tournaments",
            json={
                "name": "Bad Type",
                "start_date": "2026-06-01",
                "end_date": "2026-06-10",
                "location": "City",
                "rounds": 5,
                "type": "invalid_type_xxx",
                "status": "active",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_game_invalid_result(self, client: AsyncClient, admin_token: str):
        """Создание партии с недопустимым результатом → 422."""
        # Сначала создаём турнир и игроков
        tourn = await client.post(
            "/api/tournaments",
            json={
                "name": "Valid Tournament",
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
            json={"name": "White", "rating": 2500, "city": "City"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        p2 = await client.post(
            "/api/players",
            json={"name": "Black", "rating": 2400, "city": "City"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert p1.status_code == 201
        assert p2.status_code == 201

        resp = await client.post(
            f"/api/tournaments/{tourn_id}/games",
            json={
                "game_round": 1,
                "white_player_id": p1.json()["id"],
                "black_player_id": p2.json()["id"],
                "result": "invalid_result",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 422


class TestAuthorizationCRUD:
    """Проверка авторизации CRUD операций (разграничение admin/user)."""

    @pytest.mark.asyncio
    async def test_user_cannot_delete_player(self, client: AsyncClient, admin_token: str, user_token: str):
        """Обычный пользователь не может удалить игрока."""
        # Создаём игрока
        resp = await client.post(
            "/api/players",
            json={"name": "Delete Me", "rating": 2000, "city": "City"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 201
        player_id = resp.json()["id"]

        # Пробуем удалить как user
        resp = await client.delete(
            f"/api/players/{player_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_user_cannot_update_tournament(self, client: AsyncClient, admin_token: str, user_token: str):
        """Обычный пользователь не может изменить турнир."""
        # Создаём турнир
        resp = await client.post(
            "/api/tournaments",
            json={
                "name": "Admin Only",
                "start_date": "2026-06-01",
                "end_date": "2026-06-10",
                "location": "City",
                "rounds": 5,
                "type": "classic",
                "status": "active",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 201
        tourn_id = resp.json()["id"]

        # Пробуем обновить как user
        resp = await client.put(
            f"/api/tournaments/{tourn_id}",
            json={
                "name": "Hacked",
                "start_date": "2026-06-01",
                "end_date": "2026-06-10",
                "location": "Hacked",
                "rounds": 1,
                "type": "blitz",
                "status": "active",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp.status_code == 403
