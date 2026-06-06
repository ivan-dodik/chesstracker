# Testing Overview

## Framework
- **pytest 9.x** + **pytest-asyncio** (asyncio_mode = "auto")
- **httpx** (AsyncClient with ASGITransport)
- **pytest-cov** for coverage reports
- Total: **36 tests** (all pass)

## Test structure
```
tests/
├── conftest.py              # API test fixtures (DB override, client, tokens)
├── test_auth.py             # 4 tests: login, /me, unauthorized
├── test_players.py          # 4 tests: list, create (admin), create (user=403), get
├── test_tournaments.py      # 4 tests: list, create, get, standings
├── test_games.py            # 4 tests: list, create, update result, delete
├── test_ratings.py          # 3 tests: history, date filter, no auth
├── test_stats.py            # 4 tests: top-rated, limit, overall, head-to-head
├── test_favorites.py        # 5 tests: get, unauthorized, add+remove, duplicate, 404
├── test_activity_log.py     # 2 tests: list (admin), unauthorized
├── test_export.py           # 2 tests: export CSV, nonexistent tournament
├── test_import_route.py     # 2 tests: import CSV, invalid format
├── test_health.py           # 2 tests: health check, SSE events
├── test_auth_flow.py        # 2 tests: register + login flow
├── test_web.py              # 2 tests: dashboard page, login page
└── services/
    ├── conftest.py          # Service test fixtures (db_session, sample_*)
    ├── test_player_service.py
    ├── test_tournament_service.py
    ├── test_game_service.py
    ├── test_rating_service.py
    ├── test_favorite_service.py
    ├── test_stats_service.py
    ├── test_activity_log_service.py
    └── test_export_service.py
```

## Running tests
```bash
# All backend tests
cd backend && uv run pytest -v

# Specific file
uv run pytest -v -k "auth"

# With coverage
uv run pytest --cov

# Service tests only
uv run pytest -v tests/services/
```

## Known issues
- SQLite doesn't support JSONB → ActivityLog stores JSON as Text
- SQLite async support limited (aiosqlite works for basic usage)
- Event loop fixture needed for `asyncio_mode = "auto"` compatibility

## Links
- → `testing/fixtures.md` — conftest.py details
- → `testing/api-tests.md` — API endpoint tests
- → `testing/service-tests.md` — service layer tests
- → `backend/core-layer.md` — DB override mechanism