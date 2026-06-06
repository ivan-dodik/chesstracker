"""Tournaments API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_db
from app.models import User
from app.schemas.tournament import (
    TournamentCreate,
    TournamentList,
    TournamentRead,
    TournamentStandings,
)
from app.services import tournament_service

router = APIRouter(prefix="/api/tournaments", tags=["tournaments"])


@router.get("", response_model=TournamentList)
async def list_tournaments(
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    location: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> TournamentList:
    """Get paginated list of tournaments with optional filters."""
    tournaments, total = await tournament_service.get_tournaments(
        db, page=page, per_page=per_page, status=status, location=location,
    )
    return TournamentList(items=tournaments, total=total, page=page, per_page=per_page)


@router.post("", response_model=TournamentRead, status_code=status.HTTP_201_CREATED)
async def create_tournament(
    data: TournamentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> TournamentRead:
    """Create a new tournament (admin only)."""
    return await tournament_service.create_tournament(db, data, user_id=current_user.id)


@router.get("/{tournament_id}", response_model=TournamentRead)
async def get_tournament(
    tournament_id: int,
    db: AsyncSession = Depends(get_db),
) -> TournamentRead:
    """Get tournament details by ID."""
    tournament = await tournament_service.get_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found")
    return tournament


@router.put("/{tournament_id}", response_model=TournamentRead)
async def update_tournament(
    tournament_id: int,
    data: TournamentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> TournamentRead:
    """Update tournament details (admin only)."""
    tournament = await tournament_service.update_tournament(db, tournament_id, data, user_id=current_user.id)
    if not tournament:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found")
    return tournament


@router.delete("/{tournament_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tournament(
    tournament_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> None:
    """Delete a tournament (admin only)."""
    deleted = await tournament_service.delete_tournament(db, tournament_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found")


@router.get("/{tournament_id}/standings", response_model=list[TournamentStandings])
async def get_standings(
    tournament_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[TournamentStandings]:
    """Get tournament standings."""
    standings = await tournament_service.get_standings(db, tournament_id)
    return [TournamentStandings(**s) for s in standings]
