# Pre-commit Hooks (`.pre-commit-config.yaml`)

## Hooks

| Hook | Source | Scope | Action |
|------|--------|-------|--------|
| `ruff check (backend)` | `astral-sh/ruff-pre-commit` v0.15.16 | `^backend/` | `ruff --fix` |
| `ruff check (telegram-bot)` | `astral-sh/ruff-pre-commit` v0.15.16 | `^telegram-bot/` | `ruff --fix` |
| `pytest (backend)` | local | `^backend/` | `cd backend && uv run pytest -v --tb=short` |

## Details
- Ruff auto-fixes issues (`--fix` flag)
- Pytest runs only when backend files change
- Pytest uses `pass_filenames: false` — runs full suite, not per-file
- Telegram-bot has no pytest hook (no tests yet)

## Setup
```bash
pre-commit install
pre-commit run --all-files  # run once to verify
```

## Links
- → `infrastructure/ci.md` — CI runs same checks
- → `testing/overview.md` — pytest configuration