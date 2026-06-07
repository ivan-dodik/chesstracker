# CI/CD (`github/workflows/ci.yml`)

## Workflow triggers
- `push` to `main` branch only
- `pull_request` (any branch)

## Jobs

### `lint`
- Runs `astral-sh/ruff-action@v1` on `backend/` and `telegram-bot/`
- No additional setup needed

### `test-backend`
- **OS**: ubuntu-latest
- **Service container**: PostgreSQL 16 with health check
  - User: `ct_user`, Password: `ct_password`, DB: `ct_test`
- **Steps**:
  1. `actions/checkout@v4`
  2. `astral-sh/setup-uv@v3` with `enable-cache: true`
  3. `cd backend && uv sync && uv run pytest -v --tb=short --cov`
- **Env override**: `DATABASE_URL=postgresql+asyncpg://ct_user:ct_password@localhost/ct_test`

### `test-telegram-bot`
- **OS**: ubuntu-latest
- **Steps**:
  1. `actions/checkout@v4`
  2. `astral-sh/setup-uv@v3` with `enable-cache: true`
  3. `cd telegram-bot && uv sync && uv run pytest -v --tb=short`
- No database needed (bot has no DB dependency)

### `build` (new)
- **Needs**: `lint` (runs after lint passes)
- **Steps**:
  1. `actions/checkout@v4`
  2. `docker/setup-buildx-action@v3` — set up BuildKit
  3. `docker compose build` — build both `backend` and `telegram-bot` images
- Verifies that Docker images build successfully
- Does NOT push images to any registry

## Job graph
```
lint ─┬─ test-backend
      ├─ test-telegram-bot
      └─ build
```

## Key details
- Uses `astral-sh/setup-uv@v3` (not `actions/setup-python`)
- Backend tests use real PostgreSQL in CI (not SQLite)
- Ruff linting runs on both `backend/` and `telegram-bot/` in one step
- `build` job is independent of tests — runs in parallel with them
- `enable-cache: true` speeds up `uv sync` on subsequent runs

## Links
- → `infrastructure/docker.md` — local Docker setup
- → `infrastructure/pre-commit.md` — same checks locally
