# Telegram Bot (`telegram-bot/`)

## Status: **STUB** — not implemented yet (planned for M9)

## Current state
- `bot.py` — entry point with `main()` that only logs "starting..."
- `handlers/` — empty directory
- `services/` — empty directory

## Planned architecture (from IMPLEMENTATION_PLAN.md)

### Entry point (`bot.py`)
- Initialize `Application` (python-telegram-bot)
- Register command handlers
- Long-polling via `application.run_polling()` (not webhook)

### Handlers (`handlers/`)
- `start.py` — `/start` command: welcome message
- `subscribe.py` — `/subscribe`/`/unsubscribe`: manage chat subscriptions

### Services (`services/`)
- `api_client.py` — `httpx.AsyncClient` for backend requests
  - `GET /api/tournaments/active` — active tournaments
  - `GET /api/tournaments/{id}/games/latest` — latest results
- `notifier.py` — periodic polling of backend, sending notifications to subscribed chats

### Config (planned: `config.py`)
- `TG_BOT_TOKEN`, `BACKEND_URL` via pydantic-settings

## Docker setup
- `Dockerfile`: python:3.12-slim, uv, copies `bot.py` + handlers/ + services/
- `docker-compose.yml`: depends_on backend, env_file

## Integration with backend
- **Long-polling**: telegram-bot polls backend REST API periodically
- **No webhook**: simpler for local development (no public HTTPS URL needed)

## Links
- → `modules/api-layer.md` (backend endpoints that bot will poll)
- → `modules/docker-infra.md` (docker-compose service definition)