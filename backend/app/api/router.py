# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Main API router — combines all endpoint routers."""

from fastapi import APIRouter

from app.api.activity_log import router as activity_log_router
from app.api.auth import router as auth_router
from app.api.export import router as export_router
from app.api.favorites import router as favorites_router
from app.api.games import router as games_router
from app.api.import_route import router as import_router
from app.api.players import router as players_router
from app.api.ratings import router as ratings_router
from app.api.sse import router as sse_router
from app.api.stats import router as stats_router
from app.api.tournaments import router as tournaments_router

api_router = APIRouter()

api_router.include_router(activity_log_router)
api_router.include_router(auth_router)
api_router.include_router(export_router)
api_router.include_router(favorites_router)
api_router.include_router(games_router)
api_router.include_router(import_router)
api_router.include_router(players_router)
api_router.include_router(ratings_router)
api_router.include_router(sse_router)
api_router.include_router(stats_router)
api_router.include_router(tournaments_router)
