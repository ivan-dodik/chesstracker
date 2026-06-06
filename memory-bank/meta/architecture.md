# Architecture (`ARCHITECTURE.md`)

## System overview
```
┌──────────────────────────────────────────────────────────┐
│                    Docker Compose                         │
│  ┌─────────────────────┐    ┌──────────────────────────┐  │
│  │     Backend         │    │      Telegram-bot         │  │
│  │    (FastAPI)        │◄──►│   (python-telegram-bot)   │  │
│  │     :8000           │    │    Long-polling REST      │  │
│  │  Jinja2 + HTMX      │    └──────────────────────────┘  │
│  │  + Alpine.js        │                                   │
│  └─────────┬───────────┘                                   │
│  ┌─────────┴───────────┐                                   │
│  │     PostgreSQL 16    │                                   │
│  │     :5432            │                                   │
│  └─────────────────────┘                                   │
└──────────────────────────────────────────────────────────┘
```

## Key architectural decisions
1. **Monorepo** — all components in one repository
2. **Frontend as part of backend** — Jinja2 templates served by FastAPI
3. **Microservice for Telegram-bot** — separate container, long-polling via REST
4. **SSE instead of WebSocket** — simpler for one-way notifications
5. **JWT auth** — two pre-seeded accounts (admin, user)
6. **Package manager: `uv`** — not pip/poetry
7. **Linter: `ruff`** — flake8 + isort + pyupgrade in one
8. **Pre-commit hooks** — ruff + pytest before each commit
9. **GitHub Actions CI** — lint + test on every push/PR
10. **Test DB: SQLite** — overridden in conftest.py for isolation

## Tech stack
| Component | Technology |
|-----------|-----------|
| Backend | Python 3.12+, FastAPI, Uvicorn |
| Database | PostgreSQL 16, asyncpg |
| ORM | SQLAlchemy 2.0 (asyncio) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Frontend | Jinja2 + HTMX + Alpine.js + Chart.js |
| Telegram-bot | python-telegram-bot |
| Linter | ruff |
| CI | GitHub Actions |
| Containers | Docker, Docker Compose |

## Links
- → `backend/overview.md` — backend module map
- → `telegram-bot/overview.md` — bot architecture
- → `infrastructure/docker.md` — Docker setup
- → `infrastructure/ci.md` — CI pipeline