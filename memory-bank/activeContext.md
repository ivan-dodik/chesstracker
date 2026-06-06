# Active Context: Chess Tracker

## Текущее состояние проекта
Завершён **M5: Backend — API: специфичные фичи**. Все API эндпоинты созданы, протестированы (20/20 passed) и запушены.

## Последние изменения
- Созданы сервисы и API: rating, favorite, stats, SSE, export/import CSV, activity log
- Интегрирована запись ActivityLog во все CRUD-операции
- Интегрирована публикация SSE-событий при создании/обновлении партий
- Исправлен Dockerfile — добавлено копирование tests/
- Написаны тесты: test_ratings (3), test_stats (4), test_favorites (5)

## Следующие шаги (приоритетный порядок)
1. ✅ **M1: Архитектура и планирование** — выполнено
2. ✅ **M2: Окружение и Docker** — выполнено
3. ✅ **M3: Backend — модели и БД** — выполнено
4. ✅ **M4: Backend — API: аутентификация и базовые CRUD** — выполнено
5. ✅ **M5: Backend — API: специфичные фичи** — выполнено
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
- **SSE**: реализован in-memory pub/sub через asyncio.Queue, подходит для одного процесса
- **ActivityLog**: JSON-поля (old_values, new_values) хранятся как сериализованные строки в SQLite/PostgreSQL
