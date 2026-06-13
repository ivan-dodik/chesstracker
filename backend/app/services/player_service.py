"""Player service — business logic for player CRUD."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Player
from app.schemas.player import PlayerCreate
from app.services.activity_log_service import log_activity


async def get_players(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    name: str | None = None,
    rating_min: int | None = None,
    rating_max: int | None = None,
    city: str | None = None,
) -> tuple[list[Player], int]:
    """Get paginated list of players with optional filters."""
    query = select(Player)
    count_query = select(func.count(Player.id))

    if name:
        query = query.where(Player.name.ilike(f"%{name}%"))
        count_query = count_query.where(Player.name.ilike(f"%{name}%"))
    if rating_min is not None:
        query = query.where(Player.rating >= rating_min)
        count_query = count_query.where(Player.rating >= rating_min)
    if rating_max is not None:
        query = query.where(Player.rating <= rating_max)
        count_query = count_query.where(Player.rating <= rating_max)
    if city:
        query = query.where(Player.city.ilike(f"%{city}%"))
        count_query = count_query.where(Player.city.ilike(f"%{city}%"))

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    query = query.order_by(Player.rating.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    players = list(result.scalars().all())

    return players, total


async def get_player(db: AsyncSession, player_id: int) -> Player | None:
    """Get a single player by ID."""
    result = await db.execute(select(Player).where(Player.id == player_id))
    return result.scalar_one_or_none()


async def create_player(
    db: AsyncSession,
    data: PlayerCreate,
    user_id: int | None = None,
) -> Player:
    """Create a new player."""
    player = Player(**data.model_dump())
    db.add(player)
    await db.flush()
    await db.refresh(player)

    await log_activity(
        db, user_id, "create", "player", player.id,
        new_values=data.model_dump(),
    )

    return player


async def update_player(
    db: AsyncSession,
    player_id: int,
    data: PlayerCreate,
    user_id: int | None = None,
) -> Player | None:
    """Update an existing player."""
    player = await get_player(db, player_id)
    if not player:
        return None

    old_values = {"name": player.name, "rating": player.rating, "city": player.city}

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(player, key, value)
    await db.flush()
    await db.refresh(player)

    await log_activity(
        db, user_id, "update", "player", player_id,
        old_values=old_values,
        new_values=data.model_dump(exclude_unset=True),
    )

    return player


async def get_player_games(
    db: AsyncSession,
    player_id: int,
    page: int = 1,
    per_page: int = 50,
) -> tuple[list[dict], int]:
    """Get paginated list of games for a player with opponent names."""
    from app.models import Game

    count_query = select(func.count(Game.id)).where(
        (Game.white_player_id == player_id) | (Game.black_player_id == player_id),
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = (
        select(Game)
        .options(
            selectinload(Game.white_player),
            selectinload(Game.black_player),
            selectinload(Game.tournament),
        )
        .where(
            (Game.white_player_id == player_id) | (Game.black_player_id == player_id),
        )
        .order_by(Game.played_at.desc(), Game.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(query)
    games = list(result.scalars().all())

    enriched = []
    for g in games:
        enriched.append({
            "id": g.id,
            "tournament_id": g.tournament_id,
            "game_round": g.game_round,
            "white_player_id": g.white_player_id,
            "black_player_id": g.black_player_id,
            "white_player_name": g.white_player.name if g.white_player else None,
            "black_player_name": g.black_player.name if g.black_player else None,
            "tournament_name": g.tournament.name if g.tournament else None,
            "result": g.result,
            "played_at": g.played_at,
            "created_at": g.created_at,
        })

    return enriched, total


async def delete_player(
    db: AsyncSession,
    player_id: int,
    user_id: int | None = None,
) -> bool:
    """Delete a player by ID."""
    player = await get_player(db, player_id)
    if not player:
        return False

    old_values = {"name": player.name, "rating": player.rating, "city": player.city}

    await db.delete(player)
    await db.flush()

    await log_activity(
        db, user_id, "delete", "player", player_id,
        old_values=old_values,
    )

    return True
