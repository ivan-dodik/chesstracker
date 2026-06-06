# Environment Configuration (`.env.example`)

## Variables

| Variable | Default | Required | Purpose |
|----------|---------|----------|---------|
| `UID` | `1000` | No | User ID in containers |
| `GID` | `1000` | No | Group ID in containers |
| `DATABASE_URL` | `postgresql+asyncpg://ct_user:ct_password@db:5432/ct_database` | Yes | PostgreSQL connection |
| `SECRET_KEY` | `change-me-to-a-random-secret-key` | Yes | JWT signing key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` (24h) | No | JWT lifetime |
| `TG_BOT_TOKEN` | `""` | For bot | Telegram bot API token |
| `BACKEND_URL` | `http://backend:8000` | For bot | Backend URL for telegram-bot |
| `DEBUG` | `True` | No | Enables SQLAlchemy echo |

## Usage
```bash
# Copy template
cp .env.example .env

# Edit .env with your values
# For production, change SECRET_KEY to a random string
```

## Important
- `SECRET_KEY` must be changed in production
- `TG_BOT_TOKEN` is only needed if running telegram-bot
- `DATABASE_URL` uses `asyncpg` driver (async PostgreSQL)
- Tests override `DATABASE_URL` to SQLite automatically

## Links
- → `backend/core-layer.md` — Settings class reads these vars
- → `infrastructure/docker.md` — Docker compose uses .env file