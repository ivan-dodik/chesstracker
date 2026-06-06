"""Tournament service — business logic for tournament CRUD."""

from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Game, Player, Tournament
from app.schemas.tournament import TournamentCreate
from app.services.activity_log_service import log_activity


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


async def get_standings(db: AsyncSession, tournament_id: int) -> list[dict]:
    """Get tournament standings sorted by points."""
    result = await db.execute(
        select(Game).where(Game.tournament_id == tournament_id)
    )
    games = list(result.scalars().all())

    points: dict[int, float] = defaultdict(float)
    games_played: dict[int, int] = defaultdict(int)
    wins: dict[int, int] = defaultdict(int)
    draws: dict[int, int] = defaultdict(int)
    losses: dict[int, int] = defaultdict(int)

    for game in games:
        if not game.result:
            continue
        games_played[game.white_player_id] += 1
        games_played[game.black_player_id] += 1

        if game.result == "1-0":
            points[game.white_player_id] += 1.0
            wins[game.white_player_id] += 1
            losses[game.black_player_id] += 1
        elif game.result == "0-1":
            points[game.black_player_id] += 1.0
            wins[game.black_player_id] += 1
            losses[game.white_player_id] += 1
        else:  # ½-½
            points[game.white_player_id] += 0.5
            points[game.black_player_id] += 0.5
            draws[game.white_player_id] += 1
            draws[game.black_player_id] += 1

    # Get player names
    player_ids = set(points.keys()) | set(games_played.keys())
    standings = []
    for pid in player_ids:
        result = await db.execute(select(Player).where(Player.id == pid))
        player = result.scalar_one_or_none()
        if player:
            standings.append({
                "player_id": pid,
                "player_name": player.name,
                "points": points.get(pid, 0.0),
                "games_played": games_played.get(pid, 0),
                "wins": wins.get(pid, 0),
                "draws": draws.get(pid, 0),
                "losses": losses.get(pid, 0),
            })

    # Sort by points descending
    standings.sort(key=lambda x: (-x["points"], x["player_name"]))
    return standings
