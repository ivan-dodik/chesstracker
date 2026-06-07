"""Stats API — head-to-head, top-rated, overall statistics."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models import User
from app.schemas.player import PlayerRead
from app.services.stats_service import get_head_to_head, get_overall_stats, get_top_rated

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/head-to-head/{player1_id}/{player2_id}")
async def read_head_to_head(
    player1_id: int,
    player2_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get head-to-head statistics between two players."""
    return await get_head_to_head(db, player1_id, player2_id)


@router.get("/top-rated", response_model=list[PlayerRead])
async def read_top_rated(
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PlayerRead]:
    """Get top-rated players."""
    return await get_top_rated(db, limit)


@router.get("/overall/{player_id}")
async def read_overall_stats(
    player_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get overall statistics for a player."""
    return await get_overall_stats(db, player_id)
