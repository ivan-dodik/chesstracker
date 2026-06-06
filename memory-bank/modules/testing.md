# Testing (`tests/`)

## Framework
- **pytest 9.x** + **pytest-asyncio** + **httpx** (AsyncClient with ASGITransport)
- Asyncio mode: `auto` (in pyproject.toml)
- Total: **20 tests** (all pass)

## Test DB setup (`conftest.py`)
- `settings.DATABASE_URL` overridden to `sqlite+aiosqlite:///./test.db` **before** any app imports
- Separate `engine` + `TestSessionLocal` using SQLite
- `setup_database` fixture: creates all tables before each test, drops after
- `override_get_db()` → overrides FastAPI dependency via `app.dependency_overrides[get_db]`
- `client` fixture: `AsyncClient` with `ASGITransport(app=app)`
- Helper: `_create_user_in_test_db(username, password, role)` for test data setup

## Test fixtures

| Fixture | Purpose |
|---------|---------|
| `event_loop` | Session-scoped event loop |
| `setup_database` | Auto-used, per-test table create/drop |
| `client` | HTTP test client with DB override |
| `admin_token` | Creates admin user → returns JWT |
| `user_token` | Creates regular user → returns JWT |

## Test files (5)

| File | Tests | Coverage |
|------|-------|----------|
| `test_auth.py` | 4 | Login success, invalid password, /me with token, /me unauthorized |
| `test_players.py` | 4 | List players, create (admin), create (user=403), get by ID |
| `test_ratings.py` | 3 | Rating history, with date filter, without auth |
| `test_stats.py` | 4 | Top-rated, top-rated with limit, overall stats, head-to-head |
| `test_favorites.py` | 5 | Get favorites, unauthorized, add+remove, duplicate (409), nonexistent (404) |

## Running tests
```bash
uv run pytest -v
uv run pytest -v -k "auth"  # run specific file
```

## Known issues
- SQLite doesn't support JSONB → ActivityLog stores JSON as Text
- SQLite doesn't support async correctly in some edge cases (aiosqlite works for basic usage)
- Event loop fixture needed for `asyncio_mode = "auto"` compatibility

## Links
- → `modules/core-layer.md` (DB override mechanism)
- → `modules/api-layer.md` (endpoints tested)
- → `modules/docker-infra.md` (tests in Docker context)