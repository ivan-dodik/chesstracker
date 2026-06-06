# Services Layer (`app/services/`)

## 10 service modules

Services contain all business logic. API routers call services, never directly query models.

### `player_service.py`
| Function | Purpose | Parameters |
|----------|---------|------------|
| `get_players()` | Paginated list with search | db, page, per_page, name, rating_min, rating_max, city |
| `get_player()` | Single by ID | db, player_id |
| `create_player()` | Create + log activity | db, data (PlayerCreate), user_id |
| `update_player()` | Update + log activity | db, player_id, data, user_id |
| `delete_player()` | Delete + log activity | db, player_id, user_id |

### `tournament_service.py`
| Function | Purpose | Parameters |
|----------|---------|------------|
| `get_tournaments()` | Paginated list with filters | db, page, per_page, status, location |
| `get_tournament()` | Single by ID | db, tournament_id |
| `create_tournament()` | Create + log | db, data (TournamentCreate), user_id |
| `update_tournament()` | Update + log | db, tournament_id, data, user_id |
| `delete_tournament()` | Delete + log | db, tournament_id, user_id |
| `get_standings()` | Tournament table (points sorted) | db, tournament_id → list[dict] |

### `game_service.py`
| Function | Purpose | Parameters |
|----------|---------|------------|
| `get_games_by_tournament()` | Paginated games for tournament | db, tournament_id, page, per_page |
| `create_game()` | Create + log + SSE event | db, data (GameCreate), user_id |
| `update_game_result()` | Update result + log + SSE | db, game_id, data (GameResult), user_id |
| `delete_game()` | Delete + log | db, game_id, user_id |

### `rating_service.py`
| Function | Purpose | Parameters |
|----------|---------|------------|
| `get_rating_history()` | Rating history with date filter | db, player_id, date_from, date_to |

### `favorite_service.py`
| Function | Purpose | Parameters |
|----------|---------|------------|
| `get_favorites()` | All favorites for user | db, user_id |
| `add_favorite()` | Add (checks duplicates) | db, user_id, player_id → Favorite\|None |
| `remove_favorite()` | Remove by user+player | db, user_id, player_id → bool |

### `stats_service.py`
| Function | Purpose | Parameters |
|----------|---------|------------|
| `get_head_to_head()` | H2H between two players | db, player1_id, player2_id → dict |
| `get_top_rated()` | Top N by rating | db, limit=10 |
| `get_overall_stats()` | Wins/losses/draws for player | db, player_id → dict |

### `sse_service.py`
| Function | Purpose |
|----------|---------|
| `subscribe(event_type)` | Returns `asyncio.Queue` for subscriber |
| `unsubscribe(event_type, queue)` | Removes queue from subscribers dict |
| `publish_event(event_type, data)` | Sends JSON message to all subscribers of type + "all" |

- Global: `event_subscribers: dict[str, list[asyncio.Queue]]`
- Keepalive: ping every 30s in SSE endpoint

### `export_service.py`
| Function | Purpose |
|----------|---------|
| `export_tournament_csv(db, tournament_id)` | → CSV string or None |

### `import_service.py`
| Function | Purpose |
|----------|---------|
| `import_tournament_csv(db, tournament_id, csv_content)` | Parses 2 formats, creates games → dict summary |
| `parse_result(str)` | Normalizes result strings → `1-0`|`0-1`|`½-½`|None |
| `_find_player(db, name)` | Exact name lookup |

Supported CSV formats:
1. `round, white_player, black_player, result`
2. `round, player, opponent, result` (+ optional `color` column)

### `activity_log_service.py`
| Function | Purpose |
|----------|---------|
| `log_activity()` | Creates ActivityLog entry (called from CRUD services) |
| `get_activity_log()` | Paginated log with filters (entity_type, action, user_id, date range) |

## Cross-service calls

- `player_service`, `tournament_service`, `game_service` → call `activity_log_service.log_activity()`
- `game_service` → calls `sse_service.publish_event()`

## Links

- → `modules/api-layer.md` (each API router imports its service)
- → `modules/models-layer.md` (services query models)
- → `modules/schemas-layer.md` (services accept/return schema types)