# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Ratings API — rating history endpoints."""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models import User
from app.schemas.rating_history import RatingHistoryRead
from app.services.rating_service import get_rating_history

router = APIRouter(prefix="/api/players", tags=["ratings"])


@router.get("/{player_id}/rating-history", response_model=list[RatingHistoryRead])
async def read_rating_history(
    player_id: int,
    date_from: date | None = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: date | None = Query(None, description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[RatingHistoryRead]:
    """Get rating history for a player."""
    return await get_rating_history(db, player_id, date_from, date_to)
