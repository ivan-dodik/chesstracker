# Active Context: Chess Tracker

## Текущее состояние проекта
Проект полностью реализован. Добавлена TDD-инфраструктура. Задокументирована проблема с циклическим редиректом после логина (см. BUGS.md).

## Последние изменения
- **Обязательная авторизация (11:17)**:
  - Создан `get_current_user_for_web` в `deps.py` — поддержка `Authorization: Bearer` и cookie `jwt_token`
  - Защищены все API read endpoints (`Depends(get_current_user)`)
  - Защищены все веб-страницы, кроме `/login` (`Depends(get_current_user_for_web)`)
  - При логине устанавливается cookie `jwt_token` для прямой навигации
  - 111/111 тестов проходят
  - Все изменённые файлы: `backend/app/api/deps.py`, `web.py`, `players.py`, `tournaments.py`, `games.py`, `stats.py`, `ratings.py`, `export.py`; `backend/app/static/js/main.js`; `backend/tests/test_auth.py`, `test_web.py`, `test_players.py`, `test_tournaments.py`, `test_games.py`, `test_stats.py`, `test_ratings.py`, `test_export.py`

## Следующие шаги
- ✅ M12: TDD-инфраструктура и правила
- ✅ M13: API-тесты — Турниры, Игры, Export, Import (~24 теста)
- ✅ M14: API-тесты — Activity Log, Health, краевые случаи (~12 тестов)
- ✅ M15: Unit-тесты сервисов (~20 тестов)
- ✅ M16: Telegram-bot тесты и CI (~6 тестов)
- ✅ M17: E2E тесты Playwright (29 тестов)
- ✅ Исправить контрастность цветов CSS
- ✅ Добавить `<label>` к select элементам на дашборде
- ✅ Устранить гонку между HTMX `hx-trigger="load"` и Alpine.js `x-show` на дашборде

## Активные решения и considerations
- **Тесты**: SQLite (aiosqlite) используется для тестов вместо PostgreSQL, чтобы избежать проблем с event loop'ами. `settings.DATABASE_URL` переопределяется в conftest.py перед импортом app модулей.
- **bcrypt**: зафиксирована версия 4.0.1 из-за несовместимости passlib с bcrypt 5.x
- **Alembic**: настроен на async режим через asyncio.run()
- **Seed-данные**: пересоздают таблицы (drop_all + create_all) при каждом запуске
- **SSE**: реализован in-memory pub/sub через asyncio.Queue, подходит для одного процесса
- **ActivityLog**: JSON-поля (old_values, new_values) хранятся как сериализованные строки в SQLite/PostgreSQL
- **Jinja2**: используется кастомный Environment с cache_size=0 (обход несовместимости Jinja2 3.1.x со Starlette Jinja2Templates)
- **Шаблоны**: не используют Flask-специфичные функции (get_flashed_messages заменён на JS-управление flash-сообщениями)
- **Chart.js**: подключён через CDN (chart.umd.min.js v4.4.7), используется для line chart (история рейтинга) и doughnut chart (общая статистика)
- **Alpine.js**: компоненты ratingChart, overallStatsChart, playerDetail, tournamentDetail, headToHead, accordion
- **GameRead**: расширен полями white_player_name, black_player_name
- **TournamentStandings**: расширен полями wins, draws, losses
- **Агентские скиллы Cline**: установлены 5 пакетов (75+ скиллов). Доступны через `use_skill`. Подробнее: `memory-bank/techContext.md` (раздел «Инструменты разработки»), `.clinerules/memory-bank.md` (раздел «Установка агентских скиллов»).
- **MCP Browser Tools**: установлен `@agentdeskai/browser-tools-mcp@1.2.1` с Chrome-расширением. Инструменты: `takeScreenshot`, `getConsoleLogs`, `getConsoleErrors`, `getNetworkErrors`, `getNetworkLogs`, `runAccessibilityAudit`. Сервер работает на порту 3025.
- **Проблема аутентификации**: Частично исправлена. Корневая причина — гонка между HTMX `hx-trigger="load"` и Alpine.js `x-show`. Создан BUGS.md с полным анализом.

## Ссылки на модули

Для быстрого поиска информации используй [полный индекс](index.md).

Ключевые разделы:
- [Backend: все модули](backend/overview.md)
- [Frontend: шаблоны, CSS, JS](frontend/overview.md)
- [Telegram-bot](telegram-bot/overview.md)
- [Testing: 36 тестов](testing/overview.md)
- [Infrastructure: Docker, CI, pre-commit](infrastructure/docker.md)
- [Config: зависимости, env](config/backend-pyproject.md)
- [Meta: баги, security, архитектура](meta/bugs.md)

## 2026-06-07: E2E тесты (Playwright) — 29 тестов

**Статус:** ✅ Завершён. 29/29 E2E + 148/148 API = 177 тестов.
**Инфраструктура:** `backend/e2e/` (вне `tests/`), conftest.py с сервером + SQLite + seed.
**Проблемы:** конфликт conftest.py (решён выносом), networkidle (заменён на domcontentloaded), cookie для веб-маршрутов, Playwright Download API.
**BUGS.md:** Баг аутентификации помечен как RESOLVED.

## Итоговый статус проекта
Все майлстоуны M1–M17 завершены. 177 тестов (148 API + 29 E2E). Все требований ДЗ выполнены.
