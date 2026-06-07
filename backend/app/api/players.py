"""Players API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_current_user, get_db
from app.models import User
from app.schemas.game import GameList, GameRead
from app.schemas.player import PlayerCreate, PlayerList, PlayerRead
from app.schemas.tournament import TournamentList
from app.services import player_service, tournament_service

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
    current_user: User = Depends(get_current_user),
) -> PlayerList:
    """Get paginated list of players with optional filters."""
    players, total = await player_service.get_players(
        db, page=page, per_page=per_page,
        name=name, rating_min=rating_min, rating_max=rating_max, city=city,
    )
    return PlayerList(items=players, total=total, page=page, per_page=per_page)


@router.get("/{player_id}/games", response_model=GameList)
async def get_player_games(
    player_id: int,
    page: int = 1,
    per_page: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get paginated list of games for a player."""
    games, total = await player_service.get_player_games(
        db, player_id=player_id, page=page, per_page=per_page,
    )
    return {"items": [GameRead(**g) for g in games], "total": total, "page": page, "per_page": per_page}


@router.get("/{player_id}/tournaments", response_model=TournamentList)
async def get_player_tournaments(
    player_id: int,
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TournamentList:
    """Get paginated list of tournaments a player participated in."""
    from app.schemas.tournament import TournamentRead

    tournaments, total = await tournament_service.get_player_tournaments(
        db, player_id=player_id, page=page, per_page=per_page,
    )
    from app.models import Tournament as TournamentModel

    items = [TournamentRead.model_validate(TournamentModel(**t)) for t in tournaments]
    return TournamentList(items=items, total=total, page=page, per_page=per_page)


@router.post("", response_model=PlayerRead, status_code=status.HTTP_201_CREATED)
async def create_player(
    data: PlayerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> PlayerRead:
    """Create a new player (admin only)."""
    return await player_service.create_player(db, data, user_id=current_user.id)


@router.get("/{player_id}", response_model=PlayerRead)
async def get_player(
    player_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_admin),
) -> PlayerRead:
    """Update player details (admin only)."""
    player = await player_service.update_player(db, player_id, data, user_id=current_user.id)
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
    return player


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(
    player_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> None:
    """Delete a player (admin only)."""
    deleted = await player_service.delete_player(db, player_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
