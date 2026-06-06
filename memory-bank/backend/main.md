# Main Entry Point (`app/main.py`)

## FastAPI app setup

| Aspect | Detail |
|--------|--------|
| Title | `Chess Tracker API` |
| Version | `0.1.0` |
| Lifespan | `@asynccontextmanager` — logs start/shutdown |
| CORS | `allow_origins=["*"]` (all origins in dev) |
| Static | Mounted at `/static` from `app/static/` |
| Routers | `web_router` (Jinja2 pages) + `api_router` (REST API) |

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | `{"status": "ok"}` |

## Key details

- `BASE_DIR = Path(__file__).resolve().parent` — resolves to `app/`
- Static dir check: `if static_dir.exists()` before mount
- Router order: web_router first, then api_router (web routes take precedence)

## Links
- → `backend/api-layer.md` (api_router composition)
- → `backend/web-layer.md` (web_router routes)
- → `backend/seed.md` (seed script)