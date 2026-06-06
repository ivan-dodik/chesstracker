# Service Tests (`tests/services/`)

## Test files (8)

| File | Tests | What it covers |
|------|-------|----------------|
| `test_player_service.py` | 3 | Create player, get player by ID, get paginated list |
| `test_tournament_service.py` | 3 | Create tournament, get by ID, get standings |
| `test_game_service.py` | 3 | Create game, update result, get games by tournament |
| `test_rating_service.py` | 2 | Get rating history, with date filter |
| `test_favorite_service.py` | 4 | Add favorite, remove favorite, get favorites, duplicate add |
| `test_stats_service.py` | 3 | Get head-to-head, top-rated, overall stats |
| `test_activity_log_service.py` | 2 | Log activity, get paginated log |
| `test_export_service.py` | 2 | Export tournament CSV, nonexistent tournament |

## Common patterns

```python
async def test_create_player(db_session, sample_admin):
    player = await player_service.create_player(
        db_session,
        PlayerCreate(name="Test", rating=1500),
        sample_admin.id
    )
    assert player.name == "Test"
    assert player.rating == 1500
```

## Fixtures used
- `db_session` — clean AsyncSession per test
- `sample_player` — Player(name="Test Player", rating=1500, city="Test City")
- `sample_tournament` — Tournament(name="Test Tournament", rounds=5, type="classic", status="active")
- `sample_user` — User(username="testuser", role="user")
- `sample_admin` — User(username="admin", role="admin")

## Links
- → `testing/fixtures.md` — fixture details
- → `testing/overview.md` — test structure
- → `backend/services-layer.md` — services being tested