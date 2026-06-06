# API Tests (`tests/test_*.py`)

## Test files (14)

| File | Tests | What it covers |
|------|-------|----------------|
| `test_auth.py` | 4 | Login success, invalid password, /me with token, /me unauthorized |
| `test_players.py` | 4 | List players, create (admin), create (user=403), get by ID |
| `test_tournaments.py` | 4 | List, create, get by ID, standings |
| `test_games.py` | 4 | List by tournament, create, update result, delete |
| `test_ratings.py` | 3 | Rating history, with date_from/date_to filter, without auth |
| `test_stats.py` | 4 | Top-rated, top-rated with limit, overall stats, head-to-head |
| `test_favorites.py` | 5 | Get favorites, unauthorized, add+remove, duplicate (409), nonexistent (404) |
| `test_activity_log.py` | 2 | List log (admin), unauthorized (user=403) |
| `test_export.py` | 2 | Export CSV, nonexistent tournament (404) |
| `test_import_route.py` | 2 | Import CSV, invalid format (400) |
| `test_health.py` | 2 | Health check, SSE events endpoint |
| `test_auth_flow.py` | 2 | Register + login flow |
| `test_web.py` | 2 | Dashboard page, login page |

## Common patterns

```python
# Authenticated request
response = await client.get("/api/players", headers=admin_token)

# Unauthorized
response = await client.get("/api/activity-log")
assert response.status_code == 401

# Forbidden (user role)
response = await client.post("/api/players", headers=user_token, json={...})
assert response.status_code == 403
```

## Fixtures used
- `client` — httpx AsyncClient with ASGITransport
- `admin_token` — JWT for admin user
- `user_token` — JWT for regular user
- `setup_database` — auto-used, creates/drops tables per test

## Links
- → `testing/fixtures.md` — fixture details
- → `testing/overview.md` — test structure
- → `backend/api-layer.md` — endpoints being tested