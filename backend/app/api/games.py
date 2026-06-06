"""Games API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_db
from app.models import User
from app.schemas.game import GameCreate, GameList, GameRead, GameResult
from app.services import game_service

router = APIRouter(tags=["games"])


@router.get("/api/tournaments/{tournament_id}/games", response_model=GameList)
async def list_games(
    tournament_id: int,
    page: int = 1,
    per_page: int = 50,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get paginated list of games for a tournament."""
    games, total = await game_service.get_games_by_tournament(
        db, tournament_id=tournament_id, page=page, per_page=per_page,
    )
    return {"items": [GameRead(**g) for g in games], "total": total, "page": page, "per_page": per_page}


@router.post("/api/tournaments/{tournament_id}/games", response_model=GameRead, status_code=status.HTTP_201_CREATED)
async def create_game(
    tournament_id: int,
    data: GameCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> GameRead:
    """Create a new game (admin only)."""
    data.tournament_id = tournament_id
    return await game_service.create_game(db, data, user_id=current_user.id)


@router.put("/api/games/{game_id}", response_model=GameRead)
async def update_game_result(
    game_id: int,
    data: GameResult,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> GameRead:
    """Update game result (admin only)."""
    game = await game_service.update_game_result(db, game_id, data, user_id=current_user.id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return game


@router.delete("/api/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(
    game_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> None:
    """Delete a game (admin only)."""
    deleted = await game_service.delete_game(db, game_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
