# Schemas Layer (`app/schemas/`)

## 7 Pydantic schema files

All inherit from `BaseModel`. Read schemas use `model_config = {"from_attributes": True}` for ORM mapping.

### User (`user.py`)
- `LoginRequest`: username, password
- `UserCreate`: username, password, role (default "user")
- `UserRead`: id, username, role, created_at
- `Token`: access_token, token_type ("bearer")

### Player (`player.py`)
- `PlayerCreate`: name, rating (default 0), city (opt), avatar_url (opt)
- `PlayerRead`: id, name, rating, city, avatar_url, created_at, updated_at
- `PlayerList`: items (list[PlayerRead]), total, page, per_page

### Tournament (`tournament.py`)
- `TournamentCreate`: name, start_date, end_date, location (opt), rounds, type, status
- `TournamentRead`: id, name, start_date, end_date, location, rounds, type, status, created_at, updated_at
- `TournamentList`: items (list[TournamentRead]), total, page, per_page
- `TournamentStandings`: player_id, player_name, points, games_played

### Game (`game.py`)
- `GameCreate`: tournament_id, round, white_player_id, black_player_id, result (opt), played_at (opt)
- `GameRead`: id, tournament_id, round, white_player_id, black_player_id, result, played_at, created_at
- `GameList`: items (list[GameRead]), total, page, per_page
- `GameResult`: result (str)

### RatingHistory (`rating_history.py`)
- `RatingHistoryRead`: id, player_id, rating, date, tournament_id (opt)

### Favorite (`favorite.py`)
- `FavoriteRead`: id, user_id, player_id, created_at

### ActivityLog (`activity_log.py`)
- `ActivityLogRead`: id, user_id (opt), action, entity_type, entity_id (opt), old_values (opt dict), new_values (opt dict), timestamp

## Links

- → `modules/api-layer.md` (schemas used as response_model and request body)
- → `modules/services-layer.md` (services accept/return schemas)
- → `modules/models-layer.md` (Read schemas mirror model fields)