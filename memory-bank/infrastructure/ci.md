# CI/CD (`github/workflows/ci.yml`)

## Workflow triggers
- `on: [push, pull_request]` — runs on every push and PR

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
  2. `astral-sh/setup-uv@v3` — installs uv
  3. `cd backend && uv sync && uv run pytest -v --tb=short --cov`
- **Env override**: `DATABASE_URL=postgresql+asyncpg://ct_user:ct_password@localhost/ct_test`

### `test-telegram-bot`
- **OS**: ubuntu-latest
- **Steps**:
  1. `actions/checkout@v4`
  2. `astral-sh/setup-uv@v3`
  3. `cd telegram-bot && uv sync && uv run pytest -v --tb=short`
- No database needed (bot has no DB dependency)

## Key details
- Uses `astral-sh/setup-uv@v3` (not `actions/setup-python`)
- Backend tests use real PostgreSQL in CI (not SQLite)
- Ruff linting runs on both `backend/` and `telegram-bot/` in one step

## Links
- → `infrastructure/docker.md` — local Docker setup
- → `infrastructure/pre-commit.md` — same checks locally
- → `testing/overview.md` — test structure