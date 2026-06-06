# Telegram Bot (`telegram-bot/`)

## Status: **IMPLEMENTED** — M9 completed

## Architecture

### Entry point (`bot.py`)
- Initializes `Application` (python-telegram-bot) with `TG_BOT_TOKEN`
- Registers command handlers: `/start`, `/subscribe`, `/unsubscribe`
- Sets up `job_queue` with `Notifier.check_for_updates` every 60 seconds
- Runs long-polling via `application.run_polling()`

### Configuration (`config.py`)
- `Settings` class via pydantic-settings
- `TG_BOT_TOKEN: str` — Telegram bot token (from .env)
- `BACKEND_URL: str` — default `http://backend:8000`

### Handlers (`handlers/`)
- **`start.py`** — `/start` command: sends welcome message with command list
- **`subscribe.py`** — `/subscribe` and `/unsubscribe` commands:
  - Subscriptions stored in `subscribers.json` file (JSON array of chat IDs)
  - Functions: `subscribe_command`, `unsubscribe_command`, `get_subscribed_chats()`
  - No database dependency — simple file-based persistence

### Services (`services/`)
- **`api_client.py`** — `ApiClient` class wrapping `httpx.AsyncClient`:
  - `get_active_tournaments()` → `GET /api/tournaments?status=active`
  - `get_tournament_games(tournament_id)` → `GET /api/tournaments/{id}/games`
  - Lazy client initialization, timeout 10s
- **`notifier.py`** — `Notifier` class for background polling:
  - `check_for_updates()` called by job_queue every 60 seconds
  - Tracks known game IDs in `_known_games: set[int]` to detect new games
  - Formats notifications with HTML: tournament name, player names, results with chess emoji
  - Sends messages to all subscribed chats via `bot.send_message()`

### Docker
- `Dockerfile`: python:3.12-slim, uv, copies `bot.py`, `config.py`, `handlers/`, `services/`
- `docker-compose.yml`: depends on backend, uses env_file

## Integration with backend
- **Long-polling**: bot polls backend REST API every 60 seconds
- **No webhook**: suitable for local development (no public HTTPS URL needed)
- **Data flow**: bot calls `GET /api/tournaments?status=active` → for each tournament calls `GET /api/tournaments/{id}/games` → compares with known IDs → sends notifications

## Files
| File | Purpose |
|------|---------|
| `bot.py` | Entry point |
| `config.py` | Pydantic settings |
| `handlers/start.py` | /start handler |
| `handlers/subscribe.py` | /subscribe, /unsubscribe handlers |
| `services/api_client.py` | Backend HTTP client |
| `services/notifier.py` | Background polling notifier |

## Links
- → `backend/api-layer.md` (backend endpoints that bot polls)
- → `infrastructure/docker.md` (docker-compose service definition)