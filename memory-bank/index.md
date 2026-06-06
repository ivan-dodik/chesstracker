# Memory Bank Index

## Структура документации

```
memory-bank/
├── index.md                    ← этот файл — полный индекс
├── projectbrief.md             ← foundation document
├── productContext.md           ← why this project exists
├── activeContext.md            ← current work focus
├── systemPatterns.md           ← architecture & design patterns
├── techContext.md              ← technologies & setup
├── progress.md                 ← what works, what's left
│
├── backend/                    ← backend/app/ modules
│   ├── overview.md             ← project layout & dependency graph
│   ├── core-layer.md           ← config, database, security
│   ├── models-layer.md         ← 7 SQLAlchemy models
│   ├── schemas-layer.md        ← Pydantic schemas
│   ├── services-layer.md       ← 10 service modules
│   ├── api-layer.md            ← 12 route modules + deps
│   ├── web-layer.md            ← web.py routes
│   ├── alembic.md              ← migrations
│   ├── seed.md                 ← seed script
│   └── main.md                 ← FastAPI entry point
│
├── frontend/                   ← templates/ + static/
│   ├── overview.md             ← architecture (HTMX + Alpine + Chart.js)
│   ├── templates.md            ← all 9 templates
│   ├── css.md                  ← style.css (681 lines)
│   ├── js-main.md              ← main.js (Auth, HTMX, Alpine)
│   └── js-sse.md               ← sse.js (SSE client)
│
├── telegram-bot/               ← telegram-bot/ microservice
│   └── overview.md             ← bot architecture & handlers
│
├── testing/                    ← tests/ directory
│   ├── overview.md             ← framework & structure (36 tests)
│   ├── api-tests.md            ← 14 API test files
│   ├── service-tests.md        ← 8 service test files
│   └── fixtures.md             ← conftest.py fixtures
│
├── infrastructure/             ← Docker, CI/CD, pre-commit
│   ├── docker.md               ← docker-compose, Dockerfiles
│   ├── ci.md                   ← GitHub Actions workflow
│   └── pre-commit.md           ← pre-commit hooks
│
├── config/                     ← project configuration files
│   ├── backend-pyproject.md    ← backend/pyproject.toml
│   ├── bot-pyproject.md        ← telegram-bot/pyproject.toml
│   └── env.md                  ← .env.example
│
└── meta/                       ← project documentation & bugs
    ├── architecture.md         ← ARCHITECTURE.md summary
    ├── bugs.md                 ← BUGS.md summary
    └── security.md             ← SECURITY_AUDIT.md summary
```

## Quick lookup

| Agent needs | Read this |
|-------------|-----------|
| FastAPI app setup, lifespan | `backend/main.md` |
| DB engine, session, Base | `backend/core-layer.md` |
| JWT, password hashing | `backend/core-layer.md` |
| Pydantic settings | `backend/core-layer.md` |
| All SQLAlchemy models | `backend/models-layer.md` |
| All Pydantic schemas | `backend/schemas-layer.md` |
| API endpoints & deps | `backend/api-layer.md` |
| Web UI routes (HTML) | `backend/web-layer.md` |
| Business logic CRUD | `backend/services-layer.md` |
| Stats, ratings, favorites | `backend/services-layer.md` |
| SSE events | `backend/services-layer.md` |
| CSV export/import | `backend/services-layer.md` |
| Seed data generation | `backend/seed.md` |
| DB migration setup | `backend/alembic.md` |
| Jinja2 templates + HTMX | `frontend/templates.md` |
| CSS + JS + Alpine.js | `frontend/css.md`, `frontend/js-main.md` |
| SSE client (frontend) | `frontend/js-sse.md` |
| Telegram bot interface | `telegram-bot/overview.md` |
| Test config, fixtures | `testing/fixtures.md` |
| API tests | `testing/api-tests.md` |
| Service tests | `testing/service-tests.md` |
| Docker services, networks | `infrastructure/docker.md` |
| CI pipeline | `infrastructure/ci.md` |
| Pre-commit hooks | `infrastructure/pre-commit.md` |
| Dependencies (backend) | `config/backend-pyproject.md` |
| Dependencies (bot) | `config/bot-pyproject.md` |
| Environment variables | `config/env.md` |
| Known bugs | `meta/bugs.md` |
| Security audit | `meta/security.md` |
| Architecture overview | `meta/architecture.md` |