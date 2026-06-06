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
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI приложение
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py        # Настройки (pydantic-settings)
│   │   │   ├── database.py      # Подключение к БД
│   │   │   └── security.py      # JWT, хеширование паролей
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── player.py
│   │   │   ├── tournament.py
│   │   │   ├── game.py
│   │   │   ├── rating_history.py
│   │   │   ├── favorite.py
│   │   │   └── activity_log.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── player.py
│   │   │   ├── tournament.py
│   │   │   ├── game.py
│   │   │   └── ... (остальные схемы)
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── players.py
│   │   │   ├── tournaments.py
│   │   │   ├── games.py
│   │   │   ├── ratings.py
│   │   │   ├── favorites.py
│   │   │   ├── stats.py
│   │   │   ├── export.py
│   │   │   └── sse.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── player_service.py
│   │   │   ├── tournament_service.py
│   │   │   ├── game_service.py
│   │   │   ├── rating_service.py
│   │   │   └── ... (остальные сервисы)
│   │   ├── templates/
│   │   │   ├── base.html
│   │   │   ├── index.html
│   │   │   ├── players/
│   │   │   ├── tournaments/
│   │   │   └── auth/
│   │   └── static/
│   │       ├── css/
│   │       └── js/
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_players.py
│   │   ├── test_tournaments.py
│   │   └── ...
│   ├── Dockerfile
│   └── pyproject.toml
├── telegram-bot/
│   ├── bot.py
│   ├── handlers/
│   ├── services/
│   ├── Dockerfile
│   └── pyproject.toml
├── docker-compose.yml
├── .env.example
├── README.md
├── ARCHITECTURE.md
└── REPORT.md
```

## Технические ограничения и решения

1. **uv**: современная замена pip/poetry, быстрее, с поддержкой pyproject.toml
2. **HTMX вместо SPA-фреймворков**: серверный рендеринг с частичными обновлениями страницы
3. **Alpine.js только для реактивности клиента**: минимальный JS, без bundler'ов
4. **FastAPI + Jinja2**: единый сервер для API и HTML, упрощает деплой
5. **python-telegram-bot**: асинхронная работа, совместимость с asyncio FastAPI

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