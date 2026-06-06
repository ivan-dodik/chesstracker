"""Main API router — combines all endpoint routers."""

from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.players import router as players_router
from app.api.tournaments import router as tournaments_router
from app.api.games import router as games_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(players_router)
api_router.include_router(tournaments_router)
api_router.include_router(games_router)