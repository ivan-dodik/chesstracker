# Active Context: Chess Tracker

## Текущее состояние проекта
Проект полностью реализован. Все майлстоуны M1–M17 завершены. Дополнительно: CRUD-формы, аутентификация всех страниц, оптимизации производительности (N+1, pool, cache), множество фронтенд-фикс (hx-boost, Alpine.js/HTMX swap). В IMPLEMENTATION_PLAN.md добавлены M18–M22 (запланированы, не начаты).

**Тесты:** 189 тестов (160 API/service + 29 E2E), ruff clean.

## Последние изменения
- **CRUD-формы (2026-06-07):**
  - Созданы формы create/edit/delete для players, tournaments, games
  - 12 web-тестов для CRUD (admin/non-admin access)
  - Затронутые файлы: `templates/players/create.html`, `players/edit.html`, `tournaments/create.html`, `tournaments/edit.html`, `games/create.html`, `games/edit.html`, `tests/test_web.py`

- **Аутентификация всех страниц (2026-06-07):**
  - `get_current_user_for_web` в `deps.py` — поддержка `Authorization: Bearer` и cookie `jwt_token`
  - Защищены все API read endpoints и все веб-страницы (кроме `/login`)
  - При логине устанавливается cookie `jwt_token`
  - Затронутые файлы: `deps.py`, `web.py`, все API route-модули, `main.js`, тесты

- **Docker entrypoint (2026-06-13):**
  - `backend/entrypoint.sh` — `alembic upgrade head` + seed при пустой БД
  - `backend/Dockerfile` — COPY + CMD entrypoint.sh
  - `docker-compose.override.yml` — UVICORN_OPTS env var

- **Оптимизации производительности (2026-06-14–15):**
  - N+1 в standings → batch `WHERE id IN (...)` (31 запрос → 2)
  - `lazy="selectin"` → `lazy="raise"` на Player/Game/Tournament моделях
  - `cascade="all, delete-orphan"` на Tournament.games
  - Pool: `pool_size=10`, `max_overflow=20`, warmup 3 соединения в lifespan
  - Jinja2 `cache_size=400`
  - `SQL_ECHO` отдельный флаг от `DEBUG`
  - `pool_recycle=1800`
  - Timing middleware, file logging, async JWT decode
  - `scripts/benchmark.sh`

- **Фронтенд-фиксы (2026-06-14–15):**
  - `hx-boost="true"` — скрипты перенесены из `<head>` в `<body>` content blocks
  - Alpine.js `this._initialized` guard от двойной инициализации
  - `Alpine.initTree()` в `htmx:afterSwap` для re-init после HTMX swap
  - `Promise.all()` для параллельных fetch-запросов
  - `beforeunload` handler для закрытия SSE-соединений
  - `x-show` → `x-if` для head-to-head контейнера
  - Chart.js canvas destroy перед new Chart()

- **Code review (2026-06-14):** 22 замечания исправлены (security, performance, code quality)
- **REPORT_HUMAN.md (2026-06-18):** Человекочитаемый отчёт для преподавателя

## Следующие шаги
- [ ] M18: Исправление багов — CSV экспорт + debounce фильтрации
- [ ] M19: Расчёт рейтинга + RatingHistory (ELO formula)
- [ ] M20: SSE real-time — обновление данных на страницах
- [ ] M21: Круговая диаграмма на странице игрока
- [ ] M22: Лог активности — UI-страница + аудит рейтинга

## Активные решения и considerations
- **Тесты**: SQLite (aiosqlite) используется для тестов вместо PostgreSQL. `settings.DATABASE_URL` переопределяется в conftest.py перед импортом app модулей.
- **Models lazy="raise"**: все relationships в Player/Game/Tournament используют `lazy="raise"`. Сервисы используют явный `selectinload()` только для необходимых данных.
- **Tournament.games cascade**: `cascade="all, delete-orphan"` для корректного каскадного удаления через SQLAlchemy ORM.
- **bcrypt**: зафиксирована версия 4.0.1 из-за несовместимости passlib с bcrypt 5.x
- **Alembic**: настроен на async режим через asyncio.run()
- **Seed-данные**: пересоздают таблицы (drop_all + create_all) при каждом запуске
- **SSE**: in-memory pub/sub через asyncio.Queue, `beforeunload` handler закрывает соединения
- **Alpine.js + HTMX**: `alpine:init` event fired ОДИН раз; при HTMX swap — `Alpine.data()` напрямую + `Alpine.initTree()` в `htmx:afterSwap`
- **Chart.js**: CDN (chart.umd.min.js v4.4.7), destroy перед new Chart()
- **Pool warmup**: `SELECT 1` × 3 соединения в lifespan при старте
- **hx-boost**: скрипты в `{% block content %}` (не в `{% block extra_head %}`)
- **Агентские скиллы Cline**: установлено 32 скилла (оптимизировано с 85)
- **Playwright MCP**: `@executeautomation/playwright-mcp-server`

## Ссылки на модули

Для быстрого поиска информации используй [полный индекс](index.md).

Ключевые разделы:
- [Backend: все модули](backend/overview.md)
- [Frontend: шаблоны, CSS, JS](frontend/overview.md)
- [Telegram-bot](telegram-bot/overview.md)
- [Testing: тесты](testing/overview.md)
- [Infrastructure: Docker, CI, pre-commit](infrastructure/docker.md)
- [Config: зависимости, env](config/backend-pyproject.md)
- [Meta: баги, security, архитектура](meta/bugs.md)