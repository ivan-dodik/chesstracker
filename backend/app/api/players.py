"""Players API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user, get_db
from app.models import User
from app.schemas.player import PlayerCreate, PlayerList, PlayerRead
from app.services import player_service

router = APIRouter(prefix="/api/players", tags=["players"])


@router.get("", response_model=PlayerList)
async def list_players(
    page: int = 1,
    per_page: int = 20,
    name: str | None = None,
    rating_min: int | None = None,
    rating_max: int | None = None,
    city: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> PlayerList:
    """Get paginated list of players with optional filters."""
    players, total = await player_service.get_players(
        db, page=page, per_page=per_page,
        name=name, rating_min=rating_min, rating_max=rating_max, city=city,
    )
    return PlayerList(items=players, total=total, page=page, per_page=per_page)


@router.post("", response_model=PlayerRead, status_code=status.HTTP_201_CREATED)
async def create_player(
    data: PlayerCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> PlayerRead:
    """Create a new player (admin only)."""
    return await player_service.create_player(db, data)


@router.get("/{player_id}", response_model=PlayerRead)
async def get_player(
    player_id: int,
    db: AsyncSession = Depends(get_db),
) -> PlayerRead:
    """Get player details by ID."""
    player = await player_service.get_player(db, player_id)
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
    return player


@router.put("/{player_id}", response_model=PlayerRead)
async def update_player(
    player_id: int,
    data: PlayerCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> PlayerRead:
    """Update player details (admin only)."""
    player = await player_service.update_player(db, player_id, data)
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
    return player


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(
    player_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> None:
    """Delete a player (admin only)."""
    deleted = await player_service.delete_player(db, player_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")