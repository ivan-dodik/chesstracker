# Module Overview: Chess Tracker

## Project layout

```
chesstracker/
├── backend/                    # FastAPI backend (REST API + Web UI)
│   ├── app/
│   │   ├── core/               # Config, DB, security
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic validation schemas
│   │   ├── api/                # API & Web route handlers
│   │   ├── services/           # Business logic layer
│   │   ├── templates/          # Jinja2 HTML templates
│   │   ├── static/             # CSS, JS
│   │   ├── main.py             # FastAPI app entry point
│   │   └── seed.py             # Test data seeder
│   ├── alembic/                # DB migrations
│   ├── tests/                  # pytest tests
│   ├── Dockerfile
│   └── pyproject.toml
├── telegram-bot/               # Telegram notification microservice
│   ├── bot.py                  # Entry point (stub)
│   ├── handlers/               # Command handlers (empty)
│   ├── services/               # API client (empty)
│   ├── Dockerfile
│   └── pyproject.toml
├── docker-compose.yml
└── docker-compose.override.yml
```

## Module dependency graph

```
web.py ──► templates/ ──► static/
   │
api/* ──► services/* ──► core/deps.py ──► core/database.py
   │                        │
   │                        └── core/security.py
   │
   └── schemas/* ──────► models/* ──► core/database.py (Base)
                                  │
                                  └── alembic/env.py
```

## Quick lookup index

| Agent needs                    | Read this module file          |
|--------------------------------|--------------------------------|
| FastAPI app setup, lifespan    | modules/core-layer.md          |
| DB engine, session, Base class | modules/core-layer.md          |
| JWT, password hashing          | modules/core-layer.md          |
| Pydantic settings              | modules/core-layer.md          |
| All SQLAlchemy models          | modules/models-layer.md        |
| All Pydantic schemas           | modules/schemas-layer.md       |
| API endpoints & deps           | modules/api-layer.md           |
| Web UI routes (HTML)           | modules/api-layer.md           |
| Business logic CRUD            | modules/services-layer.md      |
| Stats, ratings, favorites      | modules/services-layer.md      |
| SSE events                     | modules/services-layer.md      |
| CSV export/import              | modules/services-layer.md      |
| Jinja2 templates + HTMX        | modules/web-layer.md           |
| CSS + JS + Alpine.js           | modules/web-layer.md           |
| DB migration setup             | modules/alembic.md             |
| Test config, fixtures          | modules/testing.md             |
| Telegram bot interface         | modules/telegram-bot.md        |
| Docker services, networks      | modules/docker-infra.md        |