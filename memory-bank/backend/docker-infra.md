# Docker Infrastructure

## Services (docker-compose.yml)

### db (postgres:16)
- Image: `postgres:16`
- Container: `chess-tracker-db`
- Env: POSTGRES_USER=ct_user, POSTGRES_PASSWORD=ct_password, POSTGRES_DB=ct_database
- Volume: `postgres_data` (persistent)
- Healthcheck: `pg_isready` every 10s
- Restart: unless-stopped

### backend (FastAPI)
- Build: `./backend/Dockerfile`
- Container: `chess-tracker-backend`
- Port: `8000:8000`
- Env: DATABASE_URL (points to db service), DEBUG=true
- Depends on: db (healthy)
- Restart: unless-stopped

### telegram-bot
- Build: `./telegram-bot/Dockerfile`
- Container: `chess-tracker-bot`
- Env: BACKEND_URL=http://backend:8000
- Depends on: backend (started)
- Restart: unless-stopped

## Override (docker-compose.override.yml — for development)

| Service | Override |
|---------|----------|
| backend | Volume mount `./backend/app:/app/app`, `--reload` flag |
| db | Exposes port `5432:5432` |
| telegram-bot | Volume mount `./telegram-bot:/app` |

## Commands

```bash
# Start all services
docker compose up --build

# Start in background
docker compose up -d

# Run seed data
docker compose run --rm backend python -m app.seed

# Run tests
docker compose run --rm backend uv run pytest -v

# Stop all
docker compose down

# Stop and remove volumes (DB reset)
docker compose down -v
```

## Network
- All services on same default network (Compose creates automatically)
- Backend accessible at `http://localhost:8000`
- DB accessible at `localhost:5432` (via override)
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment variables (`.env.example`)
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Full asyncpg connection string |
| `SECRET_KEY` | JWT signing secret |
| `TG_BOT_TOKEN` | Telegram bot token |
| `BACKEND_URL` | Backend URL for telegram-bot |
| `DEBUG` | Debug mode (SQLAlchemy echo) |

## Links
- → `modules/core-layer.md` (Config uses DATABASE_URL, etc.)
- → `modules/telegram-bot.md` (bot service config)
- → `modules/testing.md` (tests use local SQLite, not Docker)