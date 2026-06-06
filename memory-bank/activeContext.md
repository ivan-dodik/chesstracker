# Active Context: Chess Tracker

## Текущее состояние проекта
Завершён **M6: Frontend — базовая структура и навигация**. Созданы все HTML-шаблоны, CSS, JavaScript и веб-роуты. 4 страницы (дашборд, логин, игроки, турниры) возвращают HTTP 200.

## Последние изменения
- Обновлён Memory Bank: созданы файлы описания модулей в `memory-bank/modules/`
- Core-файлы Memory Bank дополнены ссылками на module-файлы

## Следующие шаги (приоритетный порядок)
1. ✅ **M1: Архитектура и планирование** — выполнено
2. ✅ **M2: Окружение и Docker** — выполнено
3. ✅ **M3: Backend — модели и БД** — выполнено
4. ✅ **M4: Backend — API: аутентификация и базовые CRUD** — выполнено
5. ✅ **M5: Backend — API: специфичные фичи** — выполнено
6. ✅ **M6: Frontend — базовая структура и навигация** (Jinja2, HTMX) — выполнено
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
- **Jinja2**: используется кастомный Environment с cache_size=0 (обход несовместимости Jinja2 3.1.x со Starlette Jinja2Templates)
- **Шаблоны**: не используют Flask-специфичные функции (get_flashed_messages заменён на JS-управление flash-сообщениями)

## Ссылки на модули

Для быстрого поиска информации:

- [Карта модулей и dependency graph](modules/overview.md)
- [Core: config, database, security](modules/core-layer.md)
- [Models: 7 SQLAlchemy моделей](modules/models-layer.md)
- [Schemas: Pydantic схемы](modules/schemas-layer.md)
- [Services: бизнес-логика](modules/services-layer.md)
- [API: все эндпоинты и deps](modules/api-layer.md)
- [Web: шаблоны, CSS, JS](modules/web-layer.md)
- [Alembic: миграции](modules/alembic.md)
- [Testing: тесты и fixtures](modules/testing.md)
- [Telegram-bot: статус и план](modules/telegram-bot.md)
- [Docker: инфраструктура](modules/docker-infra.md)