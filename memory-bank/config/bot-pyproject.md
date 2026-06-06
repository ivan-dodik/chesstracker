# Telegram Bot pyproject.toml

## Project metadata
- Name: `chesstracker-bot`
- Python: `>=3.12`
- Package manager: `uv`

## Dependencies

| Package | Purpose |
|---------|---------|
| `python-telegram-bot[job-queue]` | Telegram bot framework with job queue |
| `httpx` | HTTP client for backend API calls |
| `pydantic-settings` | Settings management |

## Dev dependencies
| Package | Purpose |
|---------|---------|
| `pytest` | Test framework |
| `pytest-asyncio` | Async test support |
| `ruff` | Linter/formatter |

## Ruff config
```toml
[tool.ruff]
target-version = "py312"
line-length = 120
```

## Links
- → `telegram-bot/overview.md` — bot architecture
- → `infrastructure/docker.md` — Dockerfile uses uv sync