# Testing Overview

## Framework
- **pytest 9.x** + **pytest-asyncio** (asyncio_mode = "auto")
- **httpx** (AsyncClient with ASGITransport)
- **pytest-cov** for coverage reports
- **Playwright** for E2E browser tests
- Total: **189 tests** (160 API/service + 29 E2E, all pass)

## Test structure
```
tests/
├── conftest.py              # API test fixtures (DB override, client, tokens)
├── test_auth.py             # Auth tests: login, /me, register
├── test_auth_flow.py        # Register + login flow
├── test_players.py          # Player CRUD tests
├── test_player_games.py     # Player games tests
├── test_player_tournaments.py # Player tournaments tests
├── test_tournaments.py      # Tournament CRUD tests
├── test_games.py            # Game CRUD tests
├── test_ratings.py          # Rating history tests
├── test_stats.py            # Stats tests
├── test_favorites.py        # Favorites tests
├── test_activity_log.py     # Activity log tests
├── test_export.py           # CSV export tests
├── test_import_route.py     # CSV import tests
├── test_health.py           # Health check tests
├── test_web.py              # Web route tests (including CRUD forms)
├── test_seed_verify.py      # Seed data verification
├── test_crud_verify.py      # CRUD verification
└── services/
    ├── test_player_service.py
    ├── test_tournament_service.py
    ├── test_game_service.py
    ├── test_rating_service.py
    ├── test_stats_service.py
    ├── test_favorite_service.py
    ├── test_activity_log_service.py
    └── test_export_service.py

e2e/
├── conftest.py              # E2E fixtures (server, browser, seed)
├── test_auth.py
├── test_dashboard.py
├── test_navigation.py
├── test_player_detail.py
├── test_players_list.py
├── test_sse.py
├── test_tournament_detail.py
└── test_tournaments_list.py
```

## Running tests
```bash
# All backend tests (API + service)
cd backend && uv run pytest -v

# E2E tests only
cd backend && uv run pytest e2e/ -v

# Specific file
uv run pytest -v -k "auth"

# With coverage
uv run pytest --cov

# Service tests only
uv run pytest -v tests/services/

# All tests including E2E
uv run pytest tests/ e2e/ -v

# Telegram-bot tests
cd telegram-bot && uv run pytest -v
```

## Known issues
- SQLite doesn't support JSONB → ActivityLog stores JSON as Text
- SQLite async support limited (aiosqlite works for basic usage)
- Event loop fixture needed for `asyncio_mode = "auto"` compatibility
- E2E tests use headless Chromium (Playwright) with separate SQLite database

## Links
- → `testing/fixtures.md` — conftest.py details
- → `testing/api-tests.md` — API endpoint tests
- → `testing/service-tests.md` — service layer tests
- → `backend/core-layer.md` — DB override mechanism