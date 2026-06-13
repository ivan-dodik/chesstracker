# Tech Context: Chess Tracker

## Технологический стек

| Компонент | Технология | Версия |
|-----------|-----------|--------|
| Backend | Python + FastAPI | 3.12+ / 0.115+ |
| Database | PostgreSQL | 16 |
| ORM | SQLAlchemy | 2.0+ |
| Миграции | Alembic | 1.13+ |
| Frontend | Jinja2 + HTMX + Alpine.js | latest |
| Графики | Chart.js | 4.x |
| Telegram-bot | python-telegram-bot | 21.x |
| Аутентификация | PyJWT | 2.x |
| Docker | Docker Compose | 3.x |
| CI | GitHub Actions | |
| Линтер | ruff | latest |
| Зависимости | uv | latest |
| Тестирование | pytest | 8.x |
| HTTP-тестирование | httpx | 0.27+ |

## Установка и запуск

### Предварительные требования
- Python 3.12+
- PostgreSQL 16 (локально или через Docker)
- Docker + Docker Compose
- uv (установка: `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Локальная разработка (без Docker)
```bash
# Установка зависимостей
uv sync

# Запуск миграций
uv run alembic upgrade head

# Запуск сервера
uv run uvicorn app.main:app --reload

# Запуск тестов
uv run pytest

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

## Структура директорий

```
chess-tracker/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI приложение
│   │   ├── core/                # Config, database, security
│   │   ├── models/              # SQLAlchemy ORM (7 моделей)
│   │   ├── schemas/             # Pydantic v2 (7 файлов)
│   │   ├── api/                 # 12 route-модулей
│   │   ├── services/            # 10 сервисов
│   │   ├── templates/           # Jinja2 (5 шаблонов + 3 partials)
│   │   ├── static/              # CSS + JS
│   │   └── seed.py              # Тестовые данные
│   ├── alembic/                 # Миграции
│   ├── tests/                   # 20 тестов
│   ├── Dockerfile
│   └── pyproject.toml
├── telegram-bot/
│   ├── bot.py                   # Stub
│   ├── handlers/                # (пусто)
│   ├── services/                # (пусто)
│   ├── Dockerfile
│   └── pyproject.toml
├── docker-compose.yml
└── docker-compose.override.yml
```

## Технические ограничения и решения

1. **uv**: современная замена pip/poetry, быстрее, с поддержкой pyproject.toml
2. **HTMX вместо SPA-фреймворков**: серверный рендеринг с частичными обновлениями страницы
3. **Alpine.js только для реактивности клиента**: минимальный JS, без bundler'ов
4. **FastAPI + Jinja2**: единый сервер для API и HTML, упрощает деплой
5. **python-telegram-bot**: асинхронная работа, совместимость с asyncio FastAPI
6. **bcrypt 4.0.1**: зафиксирована версия из-за несовместимости passlib с bcrypt 5.x

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
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
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
```

## Инструменты разработки

- **Линтер**: `ruff check .` (заменяет flake8, isort, pyupgrade)
- **Форматтер**: `ruff format .`
- **Тесты**: `pytest -v` (async через pytest-asyncio)
- **Миграции**: `alembic revision --autogenerate` / `alembic upgrade head`
- **Docker**: `docker compose up --build`
- **Агентские скиллы Cline**: установлено 32 скилла (оптимизировано с 85):
  - `mattpocock/skills` (10) — тdd, diagnose, review, improve-codebase-architecture, frontend-design, zoom-out, handoff, skill-creator, setup-pre-commit, design-an-interface
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

- [Core: config, database, security](modules/core-layer.md)
- [Models: SQLAlchemy ORM](modules/models-layer.md)
- [Schemas: Pydantic DTO](modules/schemas-layer.md)
- [Services: business logic](modules/services-layer.md)
- [API: endpoints & routing](modules/api-layer.md)
- [Web: templates, CSS, JS](modules/web-layer.md)
- [Alembic: migrations](modules/alembic.md)
- [Testing: pytest suite](modules/testing.md)
- [Telegram bot](modules/telegram-bot.md)
- [Docker infrastructure](modules/docker-infra.md)