# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Rating service — rating history for players."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RatingHistory


async def get_rating_history(
    db: AsyncSession,
    player_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[RatingHistory]:
    """Get rating history for a player with optional date filter."""
    query = select(RatingHistory).where(RatingHistory.player_id == player_id)

    if date_from:
        query = query.where(RatingHistory.date >= date_from)
    if date_to:
        query = query.where(RatingHistory.date <= date_to)

    query = query.order_by(RatingHistory.date.asc())
    result = await db.execute(query)
    return list(result.scalars().all())
