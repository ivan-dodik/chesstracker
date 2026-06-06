"""Chess Tracker Backend — FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger(__name__)


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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}