# Alembic Migrations (`alembic/`)

## Setup
- `alembic.ini` — standard config, `sqlalchemy.url` overridden in `env.py`
- `env.py` — async mode via `asyncio.run(run_async_migrations())`
  - Reads `settings.DATABASE_URL` from `app.core.config`
  - Uses `Base.metadata` from `app.models`
  - Async engine via `async_engine_from_config`

## Migration
- **1 migration**: `609ccbc113a5_initial.py`
- Creates 7 tables: `players`, `tournaments`, `users`, `games`, `rating_history`, `favorites`, `activity_logs`
- `activity_logs.old_values` / `new_values` use `postgresql.JSONB` (PostgreSQL-specific, not used in tests with SQLite)

## Commands
```bash
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
uv run alembic downgrade -1
```

## Seed data
- `app/seed.py` drops all tables, recreates them, fills with test data
- Run via: `docker compose run --rm backend python -m app.seed`
- Seed quantities: 2 users, 30 players, 10 tournaments, 225 games, 180 rating_history, 4 favorites

## Important
- `env.py` imports `from app.models import Base` — must import all models so metadata is complete
- Migration uses JSONB for PostgreSQL; model stores JSON as Text for SQLite compatibility in tests

## Links
- → `modules/models-layer.md` (models define the schema that migrations track)
- → `modules/core-layer.md` (config provides DATABASE_URL)
- → `modules/docker-infra.md` (seed command in docker context)