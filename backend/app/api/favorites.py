# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Favorites API — manage favorite players."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models import User
from app.schemas.favorite import FavoriteRead
from app.services.favorite_service import add_favorite, get_favorites, remove_favorite

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.get("", response_model=list[FavoriteRead])
async def read_favorites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[FavoriteRead]:
    """Get all favorites for the current user."""
    return await get_favorites(db, current_user.id)


@router.post("/{player_id}", response_model=FavoriteRead, status_code=status.HTTP_201_CREATED)
async def create_favorite(
    player_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FavoriteRead:
    """Add a player to favorites."""
    result = await add_favorite(db, current_user.id, player_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Player already in favorites or player not found",
        )
    return result


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite(
    player_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove a player from favorites."""
    success = await remove_favorite(db, current_user.id, player_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found",
        )
