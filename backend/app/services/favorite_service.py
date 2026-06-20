# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Favorite service — manage favorite players for users."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Favorite, Player
from app.services.activity_log_service import log_activity


async def get_favorites(
    db: AsyncSession,
    user_id: int,
) -> list[Favorite]:
    """Get all favorite players for a user."""
    query = (
        select(Favorite)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def add_favorite(
    db: AsyncSession,
    user_id: int,
    player_id: int,
) -> Favorite | None:
    """Add a player to favorites. Returns None if already exists."""
    # Check if already exists
    existing = await db.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.player_id == player_id,
        )
    )
    if existing.scalar_one_or_none():
        return None

    # Verify player exists
    player_exists = await db.execute(
        select(Player).where(Player.id == player_id)
    )
    if not player_exists.scalar_one_or_none():
        return None

    favorite = Favorite(user_id=user_id, player_id=player_id)
    db.add(favorite)
    await db.flush()
    await db.refresh(favorite)

    await log_activity(
        db, user_id, "create", "favorite", favorite.id,
        new_values={"player_id": player_id, "user_id": user_id},
    )

    return favorite


async def remove_favorite(
    db: AsyncSession,
    user_id: int,
    player_id: int,
) -> bool:
    """Remove a player from favorites."""
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.player_id == player_id,
        )
    )
    favorite = result.scalar_one_or_none()
    if not favorite:
        return False
    await db.delete(favorite)
    await db.flush()

    await log_activity(
        db, user_id, "delete", "favorite", favorite.id,
        old_values={"player_id": player_id, "user_id": user_id},
    )

    return True
