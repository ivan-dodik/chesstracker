# Docker Infrastructure

## Services (`docker-compose.yml`)

| Service | Image | Port | Depends on |
|---------|-------|------|------------|
| `db` | postgres:16 | 5432 | — |
| `backend` | chesstracker-backend (build) | 8000 | db |
| `telegram-bot` | chesstracker-bot (build) | — | backend |

## Environment variables (`.env`)

| Variable | Default | Purpose |
|----------|---------|---------|
| `UID` / `GID` | 1000 / 1000 | User in containers |
| `DATABASE_URL` | `postgresql+asyncpg://ct_user:ct_password@db:5432/ct_database` | DB connection |
| `SECRET_KEY` | `change-me-to-a-random-secret-key` | JWT signing |
| `TG_BOT_TOKEN` | `""` | Telegram bot token |
| `BACKEND_URL` | `http://backend:8000` | Used by telegram-bot |
| `DEBUG` | `True` | SQLAlchemy echo |

## Dockerfiles

### `backend/Dockerfile`
- Base: `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` (uv предустановлен)
- BuildKit cache mount: `--mount=type=cache,target=/root/.cache/uv`
- Copies `pyproject.toml`, `uv.lock`, then `app/`, `alembic/`, `entrypoint.sh`
- Command: `./entrypoint.sh` (alembic migrations → seed check → uvicorn)
- Прямой вызов `.venv/bin/` вместо `uv run` (без dev-deps)

### `telegram-bot/Dockerfile`
- Base: `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` (uv предустановлен)
- BuildKit cache mount: `--mount=type=cache,target=/root/.cache/uv`
- Copies `pyproject.toml`, `uv.lock`, then `bot.py`, `config.py`, `handlers/`, `services/`
- Command: `.venv/bin/python bot.py` (прямой вызов без uv run)

## Override (`docker-compose.override.yml`)
- Mounts volumes for hot reload: `./backend/app:/app/app`
- Sets `DEBUG=true` with `--reload`

## Useful commands
```bash
# Start all services (parallel build)
docker compose build --parallel && docker compose up -d

# View logs
docker compose logs -f backend

# Run tests (outside Docker)
cd backend && uv run pytest -v

# Ruff check
cd backend && uv run ruff check && cd ../telegram-bot && uv run ruff check
```

## Optimization (2026-06-14)
- Base image: `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` (no pip install)
- BuildKit cache mounts for uv packages
- PostgreSQL healthcheck: interval 2s, start_period 5s
- Direct `.venv/bin/` calls instead of `uv run` (no dev-deps download)
- Extended `.dockerignore` (memory-bank, scripts, .venv, *.pyc)

## Links
- → `backend/core-layer.md` — config.py reads env vars
- → `telegram-bot/overview.md` — bot Dockerfile
- → `infrastructure/ci.md` — CI uses same PostgreSQL image