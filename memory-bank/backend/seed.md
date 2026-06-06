# Seed Script (`app/seed.py`)

## Purpose
Generates test data for development. Drops all tables, recreates them, fills with realistic chess data.

## Data pools

| Pool | Count | Source |
|------|-------|--------|
| First names | 30 | Magnus, Ian, Hikaru, Fabiano, Ding, ... |
| Last names | 30 | Carlsen, Nepomniachtchi, Nakamura, ... |
| Cities | 20 | Moscow, Saint Petersburg, Novosibirsk, ... |
| Tournaments | 10 | Moscow Chess Championship, Saint Petersburg Rapid, ... |

## Generated data

| Entity | Quantity | Details |
|--------|----------|---------|
| Users | 2 | admin/admin123 (role=admin), user/user123 (role=user) |
| Players | 30 | Random name, rating 1500-2800, random city |
| Tournaments | 10 | 3 completed, 7 active; types: classic/rapid/blitz |
| Games | 200+ | Random pairings, weighted results (40% 1-0, 30% 0-1, 30% ½-½) |
| RatingHistory | 180 | 6 months of history per player, delta ±15 |
| Favorites | 4 | user→players[0,1,2], admin→players[3] |
| ActivityLogs | 3 | create tournament, create player, add favorite |

## Key functions

| Function | Purpose |
|----------|---------|
| `generate_rating_change(current_rating)` | Random delta -15..+15, clamped ≥0 |
| `random_games_for_tournament(players, tournament_id, rounds, start_date)` | Generates round-robin style games with unique pairs |

## Run command
```bash
docker compose run --rm backend python -m app.seed
```

## Important
- Uses `Base.metadata.drop_all` + `create_all` — destructive, wipes all data
- Runs inside `async with engine.begin()` for DDL, then `async_session_factory()` for data
- Passwords hashed via `hash_password()` from `core/security.py`

## Links
- → `backend/core-layer.md` (database engine, security)
- → `backend/models-layer.md` (all 7 models used)
- → `backend/alembic.md` (migrations create same schema)