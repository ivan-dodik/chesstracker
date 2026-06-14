# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Tournament service — business logic for tournament CRUD."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Tournament
from app.schemas.tournament import TournamentCreate
from app.services.activity_log_service import log_activity
from app.services.standings_service import calculate_standings


async def get_tournaments(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    location: str | None = None,
) -> tuple[list[Tournament], int]:
    """Get paginated list of tournaments with optional filters."""
    query = select(Tournament)
    count_query = select(func.count(Tournament.id))

    if status:
        query = query.where(Tournament.status == status)
        count_query = count_query.where(Tournament.status == status)
    if location:
        query = query.where(Tournament.location.ilike(f"%{location}%"))
        count_query = count_query.where(Tournament.location.ilike(f"%{location}%"))

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Tournament.start_date.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    tournaments = list(result.scalars().all())

    return tournaments, total


async def get_tournament(db: AsyncSession, tournament_id: int) -> Tournament | None:
    """Get a single tournament by ID."""
    result = await db.execute(select(Tournament).where(Tournament.id == tournament_id))
    return result.scalar_one_or_none()


async def create_tournament(
    db: AsyncSession,
    data: TournamentCreate,
    user_id: int | None = None,
) -> Tournament:
    """Create a new tournament."""
    tournament = Tournament(**data.model_dump())
    db.add(tournament)
    await db.flush()
    await db.refresh(tournament)

    await log_activity(
        db, user_id, "create", "tournament", tournament.id,
        new_values=data.model_dump(),
    )

    return tournament


async def update_tournament(
    db: AsyncSession,
    tournament_id: int,
    data: TournamentCreate,
    user_id: int | None = None,
) -> Tournament | None:
    """Update an existing tournament."""
    tournament = await get_tournament(db, tournament_id)
    if not tournament:
        return None

    old_values = {
        "name": tournament.name, "start_date": str(tournament.start_date),
        "end_date": str(tournament.end_date), "location": tournament.location,
    }

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(tournament, key, value)
    await db.flush()
    await db.refresh(tournament)

    await log_activity(
        db, user_id, "update", "tournament", tournament_id,
        old_values=old_values,
        new_values=data.model_dump(exclude_unset=True),
    )

    return tournament


async def delete_tournament(
    db: AsyncSession,
    tournament_id: int,
    user_id: int | None = None,
) -> bool:
    """Delete a tournament by ID."""
    tournament = await get_tournament(db, tournament_id)
    if not tournament:
        return False

    old_values = {"name": tournament.name, "status": tournament.status}

    await db.delete(tournament)
    await db.flush()

    await log_activity(
        db, user_id, "delete", "tournament", tournament_id,
        old_values=old_values,
    )

    return True


async def get_player_tournaments(
    db: AsyncSession,
    player_id: int,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[dict], int]:
    """Get paginated list of tournaments a player participated in."""
    from app.models import Game, Tournament

    # Get distinct tournament IDs where this player has games
    tids_query = (
        select(Game.tournament_id)
        .where(
            (Game.white_player_id == player_id) | (Game.black_player_id == player_id),
        )
        .distinct()
        .subquery()
    )

    count_query = select(func.count()).select_from(tids_query)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = (
        select(Tournament)
        .where(Tournament.id.in_(select(tids_query.c.tournament_id)))
        .order_by(Tournament.start_date.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(query)
    tournaments = list(result.scalars().all())

    enriched = []
    for t in tournaments:
        enriched.append({
            "id": t.id,
            "name": t.name,
            "start_date": t.start_date,
            "end_date": t.end_date,
            "location": t.location,
            "rounds": t.rounds,
            "type": t.type,
            "status": t.status,
            "created_at": t.created_at,
            "updated_at": t.updated_at,
        })

    return enriched, total


async def get_standings(db: AsyncSession, tournament_id: int) -> list[dict]:
    """Get tournament standings sorted by points."""
    return await calculate_standings(db, tournament_id)
