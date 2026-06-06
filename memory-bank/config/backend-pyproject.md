# Backend pyproject.toml

## Project metadata
- Name: `chesstracker-backend`
- Python: `>=3.12`
- Package manager: `uv`

## Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi[standard]` | Web framework |
| `uvicorn[standard]` | ASGI server |
| `sqlalchemy[asyncio]` | ORM |
| `asyncpg` | PostgreSQL async driver |
| `aiosqlite` | SQLite async driver (dev/test) |
| `alembic` | DB migrations |
| `pydantic-settings` | Settings management |
| `python-jose[cryptography]` | JWT tokens |
| `passlib[bcrypt]` | Password hashing |
| `bcrypt==4.0.1` | Pinned due to passlib incompatibility with 5.x |
| `jinja2` | Template engine |
| `aiofiles` | Static file serving |
| `python-multipart` | File upload support |
| `httpx` | HTTP client (tests) |

## Dev dependencies
| Package | Purpose |
|---------|---------|
| `pytest` | Test framework |
| `pytest-asyncio` | Async test support |
| `pytest-cov` | Coverage reports |
| `ruff` | Linter/formatter |

## Test config
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-v --tb=short"
```

## Ruff config
```toml
[tool.ruff]
target-version = "py312"
line-length = 120
```

## Links
- → `infrastructure/docker.md` — Dockerfile uses uv sync
- → `infrastructure/ci.md` — CI runs uv sync
- → `testing/overview.md` — pytest config