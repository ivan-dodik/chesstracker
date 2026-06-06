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
- Base: `python:3.12-slim`
- Package manager: `uv` (installed via pip)
- Copies `pyproject.toml`, `uv.lock`, then `app/` directory
- Command: `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000`

### `telegram-bot/Dockerfile`
- Base: `python:3.12-slim`
- Package manager: `uv`
- Copies `pyproject.toml`, `uv.lock`, then `bot.py`, `config.py`, `handlers/`, `services/`
- Command: `uv run python bot.py`

## Override (`docker-compose.override.yml`)
- Mounts volumes for hot reload: `./backend/app:/app/app`, `./telegram-bot:/app`
- Sets `DEBUG=true`

## Useful commands
```bash
# Start all services
docker compose up -d

# Run seed data
docker compose run --rm backend python -m app.seed

# Run tests
docker compose run --rm backend uv run pytest -v

# View logs
docker compose logs -f backend
```

## Links
- → `backend/core-layer.md` — config.py reads env vars
- → `telegram-bot/overview.md` — bot Dockerfile
- → `infrastructure/ci.md` — CI uses same PostgreSQL image