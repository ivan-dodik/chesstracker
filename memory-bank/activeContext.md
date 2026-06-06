# Active Context: Chess Tracker

## Текущее состояние проекта
Завершён **M4: Backend — API: аутентификация и базовые CRUD**. Все API эндпоинты созданы, протестированы (8/8 passed) и проверены через Docker Compose.

## Последние изменения
- Исправлен `backend/tests/conftest.py` — `settings.DATABASE_URL` переопределяется до импорта `database.py`, что предотвращает подключение к PostgreSQL во время тестов
- Добавлена вспомогательная функция `_create_user_in_test_db` для создания пользователей в тестовой БД
- Проверены все API эндпоинты M4 через Docker Compose (health, login, me, players CRUD, tournaments CRUD, games CRUD, standings)

## Следующие шаги (приоритетный порядок)
1. ✅ **M1: Архитектура и планирование** — выполнено
2. ✅ **M2: Окружение и Docker** — выполнено
3. ✅ **M3: Backend — модели и БД** — выполнено
4. ✅ **M4: Backend — API: аутентификация и базовые CRUD** — выполнено
5. **M5: Backend — API: специфичные фичи**
   - Ratings: `GET /api/players/{id}/rating-history`
   - Favorites: CRUD для избранного
   - Stats: head-to-head, top-rated, overall
   - SSE: `GET /api/events`
   - Export/Import CSV
   - ActivityLog
   - Тесты (3–4)
6. **M6: Frontend — базовая структура и навигация** (Jinja2, HTMX)
7. **M7: Frontend — дашборд и детальные страницы** (Chart.js, Alpine.js)
8. **M8: Frontend — фичи** (избранное, SSE, CSV, аутентификация)
9. **M9: Telegram-bot** (long-polling)
10. **M10: Тестирование и CI** (GitHub Actions, ruff, pytest)
11. **M11: Финальная документация** (README.md, REPORT.md)

## Активные решения и considerations
- **Тесты**: SQLite (aiosqlite) используется для тестов вместо PostgreSQL, чтобы избежать проблем с event loop'ами. `settings.DATABASE_URL` переопределяется в conftest.py перед импортом app модулей.
- **bcrypt**: зафиксирована версия 4.0.1 из-за несовместимости passlib с bcrypt 5.x
- **Alembic**: настроен на async режим через asyncio.run()
- **Seed-данные**: пересоздают таблицы (drop_all + create_all) при каждом запуске