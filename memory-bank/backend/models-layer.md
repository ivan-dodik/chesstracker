# Models Layer (`app/models/`)

## 7 SQLAlchemy models

All models inherit from `Base` (`core/database.py`). All use `lazy="selectin"` for relationships.

### User (`user.py`)
- Table: `users`
- Fields: `id (PK)`, `username (unique, indexed)`, `hashed_password`, `role` (`admin`|`user`), `created_at`
- Relations: `favorites → Favorite`, `activity_logs → ActivityLog`

### Player (`player.py`)
- Table: `players`
- Fields: `id (PK, indexed)`, `name (indexed)`, `rating`, `city`, `avatar_url`, `created_at`, `updated_at`
- Relations: `games_as_white → Game`, `games_as_black → Game`, `rating_history → RatingHistory`, `favorites → Favorite`

### Tournament (`tournament.py`)
- Table: `tournaments`
- Fields: `id (PK, indexed)`, `name`, `start_date`, `end_date`, `location`, `rounds`, `type` (`classic`|`blitz`|`rapid`), `status` (`active`|`completed`), `created_at`, `updated_at`
- Relations: `games → Game`

### Game (`game.py`)
- Table: `games`
- Fields: `id (PK, indexed)`, `tournament_id (FK→tournaments, indexed)`, `round`, `white_player_id (FK→players, indexed)`, `black_player_id (FK→players, indexed)`, `result` (`1-0`|`0-1`|`½-½`), `played_at`, `created_at`
- Relations: `tournament → Tournament`, `white_player → Player`, `black_player → Player`

### RatingHistory (`rating_history.py`)
- Table: `rating_history`
- Fields: `id (PK, indexed)`, `player_id (FK→players, indexed)`, `rating`, `date`, `tournament_id (FK→tournaments, nullable)`
- Relations: `player → Player`

### Favorite (`favorite.py`)
- Table: `favorites`
- Fields: `id (PK, indexed)`, `user_id (FK→users)`, `player_id (FK→players)`, `created_at`
- Constraints: `UNIQUE(user_id, player_id)` — `uq_user_player_favorite`
- Relations: `user → User`, `player → Player`

### ActivityLog (`activity_log.py`)
- Table: `activity_logs`
- Fields: `id (PK, indexed)`, `user_id (FK→users, SET NULL, indexed)`, `action`, `entity_type`, `entity_id`, `old_values` (JSON string via `Text` column), `new_values` (JSON string), `timestamp`
- Methods: `set_old_values(dict)`, `get_old_values() → dict`, `set_new_values(dict)`, `get_new_values() → dict`
- Relations: `user → User`

## Important notes

- **JSON storage**: ActivityLog stores JSON as serialized strings in `Text` columns (not JSONB) for SQLite compatibility in tests
- **ondelete behavior**: `CASCADE` for most FKs, `SET NULL` for `activity_logs.user_id`
- **indexes**: All foreign keys are indexed. `players.name` has a separate index for ILIKE search
- **Enums**: `tournament_type`, `tournament_status`, `game_result`, `user_role` — SQLAlchemy Enum types

## Links

- → `modules/core-layer.md` (Base, import path)
- → `modules/schemas-layer.md` (Pydantic mirrors of models)
- → `modules/services-layer.md` (services query these models)
- → `modules/alembic.md` (migrations reference metadata)