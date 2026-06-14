# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Chess Tracker Backend — FastAPI application entry point."""

import logging
import logging.handlers
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import text

from app.api.deps import RedirectToLoginError
from app.api.router import api_router
from app.api.web import router as web_router
from app.core.config import settings
from app.core.database import engine
from app.middleware.timing import TimingMiddleware

logger = logging.getLogger(__name__)

# ── File logging setup ──────────────────────────────────────────────
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
_log_handlers: list[logging.Handler] = [logging.StreamHandler()]

try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE = LOG_DIR / "backend.log"
    file_handler = logging.handlers.RotatingFileHandler(
        str(LOG_FILE), maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)-7s %(name)s — %(message)s"),
    )
    _log_handlers.append(file_handler)
except OSError as exc:
    # Container volume may not be writable (e.g. permission denied on host dir).
    # Fall back to stderr-only logging so the app still starts.
    print(f"WARNING: Cannot create log file ({exc}). Logging to stderr only.")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-7s %(name)s — %(message)s",
    handlers=_log_handlers,
)

# Quieten noisy libraries
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context."""
    logger.info("Starting Chess Tracker Backend...")
    # Warmup DB connection pool (fill 3 of 10 slots to avoid cold-start latency)
    for _ in range(3):
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    logger.info("Database pool warmed up (3 connections).")

    # Warmup Jinja2 templates — compile all templates on startup to avoid
    # ~50s first-request latency from lazy compilation in Docker overlay fs.
    from app.api.web import env
    for tpl_name in env.list_templates():
        env.get_template(tpl_name)
    logger.info("Jinja2 templates warmed up (%d templates).", len(list(env.list_templates())))

    yield
    await engine.dispose()
    logger.info("Shutting down Chess Tracker Backend...")


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Chess Tracker API",
    description="API for tracking chess tournaments, players and ratings",
    version="0.1.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Timing middleware (outermost — measures total request time)
app.add_middleware(TimingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Static files
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Register exception handler for RedirectToLoginError
@app.exception_handler(RedirectToLoginError)
async def redirect_to_login_handler(
    request: Request, exc: RedirectToLoginError,
) -> RedirectResponse:
    """Redirect unauthenticated web requests to /login."""
    return RedirectResponse(url="/login", status_code=303)

# Web page router (Jinja2 templates)
app.include_router(web_router)

# API router
app.include_router(api_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
