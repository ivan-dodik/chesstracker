# Tech Context: Chess Tracker

## Технологический стек

| Компонент | Технология | Версия |
|-----------|-----------|--------|
| Backend | Python + FastAPI | 3.12+ / 0.115+ |
| Database | PostgreSQL | 16 |
| ORM | SQLAlchemy | 2.0+ |
| Миграции | Alembic | 1.13+ |
| Frontend | Jinja2 + HTMX + Alpine.js | latest |
| Графики | ApexCharts | 3.54 |
| Telegram-bot | python-telegram-bot | 21.x |
| Аутентификация | PyJWT + python-jose | 2.x |
| Docker | Docker Compose | 3.x |
| CI | GitHub Actions | |
| Линтер | ruff | latest |
| Зависимости | uv | latest |
| Тестирование | pytest | 8.x |
| HTTP-тестирование | httpx | 0.27+ |
| E2E тестирование | Playwright | latest |

## Установка и запуск

### Предварительные требования
- Python 3.12+
- PostgreSQL 16 (локально или через Docker)
- Docker + Docker Compose
- uv (установка: `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Локальная разработка (без Docker)
```bash
# Установка зависимостей
cd backend && uv sync

# Запуск миграций
uv run alembic upgrade head

# Запуск seed (опционально)
uv run python -m app.seed

# Запуск сервера
uv run uvicorn app.main:app --reload

# Запуск тестов
uv run pytest -v

# Линтер
uv run ruff check .
```

### Запуск через Docker Compose
```bash
docker compose up --build
```

После запуска:
- Backend: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- PostgreSQL: localhost:5432
- Автоматические миграции + seed при первом запуске (entrypoint.sh)

## Структура директорий

```
chesstracker/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI приложение + lifespan
│   │   ├── seed.py              # Тестовые данные
│   │   ├── core/                # Config, database, security
│   │   ├── models/              # SQLAlchemy ORM (7 моделей)
│   │   ├── schemas/             # Pydantic v2 (7 файлов)
│   │   ├── api/                 # 14 route-модулей (включая deps, web, import_route, activity_log)
│   │   ├── services/            # Бизнес-логика
│   │   ├── middleware/          # Timing middleware
│   │   ├── templates/           # Jinja2 (17 шаблонов + partials)
│   │   └── static/              # CSS + JS (main.js, sse.js)
│   ├── alembic/                 # Миграции
│   ├── tests/                   # API + service тесты
│   ├── e2e/                     # E2E тесты (Playwright)
│   ├── entrypoint.sh            # Docker entrypoint (миграции + seed)
│   ├── Dockerfile
│   └── pyproject.toml
├── telegram-bot/
│   ├── bot.py                   # Точка входа
│   ├── config.py                # Pydantic BaseSettings
│   ├── handlers/                # /start, /subscribe, /unsubscribe
│   ├── services/                # api_client, notifier
│   ├── tests/                   # Тесты (api_client, notifier)
│   ├── Dockerfile
│   └── pyproject.toml
├── .github/workflows/ci.yml     # GitHub Actions CI
├── .pre-commit-config.yaml      # Pre-commit hooks
├── docker-compose.yml
├── docker-compose.override.yml
├── scripts/
│   ├── benchmark.sh             # Скрипт бенчмарка
│   └── run_e2e.py               # Запуск E2E тестов
└── memory-bank/                 # Документация для агента
```

## Технические ограничения и решения

1. **uv**: современная замена pip/poetry, быстрее, с поддержкой pyproject.toml
2. **HTMX вместо SPA-фреймворков**: серверный рендеринг с частичными обновлениями страницы
3. **Alpine.js только для реактивности клиента**: минимальный JS, без bundler'ов
4. **FastAPI + Jinja2**: единый сервер для API и HTML, упрощает деплой
5. **python-telegram-bot**: асинхронная работа, совместимость с asyncio FastAPI
6. **bcrypt 4.0.1**: зафиксирована версия из-за несовместимости passlib с bcrypt 5.x
7. **Jinja2 cache_size=400**: обход несовместимости Starlette Jinja2Templates с Jinja2 3.1.x
8. **lazy="raise"**: предотвращает N+1; явный selectinload() в сервисах
9. **hx-boost + Alpine.js**: скрипты в `{% block content %}` (не в `{% block extra_head %}`)
10. **Pool warmup**: `SELECT 1` × 3 соединения в lifespan для cold start
11. **SQL_ECHO**: отдельный флаг от DEBUG, чтобы не спамить SQL-логами
12. **Rate limiting**: slowapi для ограничения частоты запросов
13. **File logging**: RotatingFileHandler для backend логов

## Зависимости

### Backend (pyproject.toml)
```toml
[project]
name = "chess-tracker-backend"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "sqlalchemy>=2.0",
    "alembic>=1.13",
    "asyncpg>=0.30",
    "psycopg2-binary>=2.9",
    "python-jose[cryptography]>=3.3",
    "passlib[bcrypt]>=1.7",
    "jinja2>=3.1",
    "python-multipart>=0.0",
    "python-dotenv>=1.0",
    "pydantic-settings>=2.5",
    "httpx>=0.27",
    "sse-starlette>=2.0",
    "slowapi>=0.1",
    "aiofiles>=23.0",
    "bcrypt>=4.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "pytest-cov>=5.0",
    "httpx>=0.27",
    "ruff>=0.5",
]
```

### Telegram-bot (pyproject.toml)
```toml
[project]
name = "chess-tracker-bot"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "python-telegram-bot>=21",
    "httpx>=0.27",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "pytest-httpx>=0.30",
    "ruff>=0.5",
]
```

## Инструменты разработки

- **Линтер**: `ruff check .` (заменяет flake8, isort, pyupgrade)
- **Форматтер**: `ruff format .`
- **Тесты**: `pytest -v` (async через pytest-asyncio)
- **E2E тесты**: `python scripts/run_e2e.py`
- **Миграции**: `alembic revision --autogenerate` / `alembic upgrade head`
- **Docker**: `docker compose up --build`
- **Бенчмарк**: `scripts/benchmark.sh`
- **Агентские скиллы Cline**: установлено 32 скилла:
  - `mattpocock/skills` (10) — tdd, diagnose, review, improve-codebase-architecture, frontend-design, zoom-out, handoff, skill-creator, setup-pre-commit, design-an-interface
  - `obra/superpowers` (7) — brainstorming, writing-plans, executing-plans, finishing-a-development-branch, using-git-worktrees, verification-before-completion, dispatching-parallel-agents, subagent-driven-development
  - `mindrally/skills` (5) — fastapi-python, postgresql-best-practices, python-testing, htmx, docker, security-best-practices, web-scraping
  - `anthropics/skills` (3) — doc-coauthoring, skill-creator, webapp-testing
  - `xixu-me/skills` (3) — github-actions-docs, readme-i18n, skills-cli
  - `brettatoms/agent-skills` (1) — alpinejs
  - Always-on: `caveman` (компактный стиль общения)
  - Файл конфигурации: `skills-lock.json` (32 скилла)
  - Индекс: `skills-index.md` (каталог с триггерами)
  - Правило: `.clinerules/skills-usage.md` (caveman always-on, маппинг контекст→скилл)

## Ссылки на модули

Детальное описание технологии каждого слоя:

- [Core: config, database, security](backend/core-layer.md)
- [Models: SQLAlchemy ORM](backend/models-layer.md)
- [Schemas: Pydantic DTO](backend/schemas-layer.md)
- [Services: business logic](backend/services-layer.md)
- [API: endpoints & routing](backend/api-layer.md)
- [Web: templates, CSS, JS](backend/web-layer.md)
- [Alembic: migrations](backend/alembic.md)
- [Testing: pytest suite](testing/overview.md)
- [Telegram bot](telegram-bot/overview.md)
- [Docker infrastructure](infrastructure/docker.md)