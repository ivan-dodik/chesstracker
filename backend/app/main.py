"""Chess Tracker Backend — FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.deps import RedirectToLoginError
from app.api.router import api_router
from app.api.web import router as web_router

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context."""
    logger.info("Starting Chess Tracker Backend...")
    yield
    logger.info("Shutting down Chess Tracker Backend...")


app = FastAPI(
    title="Chess Tracker API",
    description="API for tracking chess tournaments, players and ratings",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
# In production, restrict allow_origins to specific domains
CORS_ORIGINS = ["*"]  # Allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
