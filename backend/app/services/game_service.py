"""Game service — business logic for game CRUD."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Game, Player
from app.schemas.game import GameCreate, GameResult
from app.services.activity_log_service import log_activity
from app.services.sse_service import publish_event


async def get_games_by_tournament(
    db: AsyncSession,
    tournament_id: int,
    page: int = 1,
    per_page: int = 50,
) -> tuple[list[dict], int]:
    """Get paginated list of games for a tournament."""
    count_query = select(func.count(Game.id)).where(Game.tournament_id == tournament_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = (
        select(Game)
        .where(Game.tournament_id == tournament_id)
        .order_by(Game.round, Game.id)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(query)
    games = list(result.scalars().all())

    # Enrich with player names
    enriched = []
    for g in games:
        white_name = None
        black_name = None
        if g.white_player_id:
            wp = await db.execute(select(Player).where(Player.id == g.white_player_id))
            w = wp.scalar_one_or_none()
            white_name = w.name if w else None
        if g.black_player_id:
            bp = await db.execute(select(Player).where(Player.id == g.black_player_id))
            b = bp.scalar_one_or_none()
            black_name = b.name if b else None
        enriched.append({
            "id": g.id,
            "tournament_id": g.tournament_id,
            "round": g.round,
            "white_player_id": g.white_player_id,
            "black_player_id": g.black_player_id,
            "white_player_name": white_name,
            "black_player_name": black_name,
            "result": g.result,
            "played_at": g.played_at,
            "created_at": g.created_at,
        })

    return enriched, total


async def create_game(
    db: AsyncSession,
    data: GameCreate,
    user_id: int | None = None,
) -> Game:
    """Create a new game."""
    game = Game(**data.model_dump())
    db.add(game)
    await db.flush()
    await db.refresh(game)

    await log_activity(
        db, user_id, "create", "game", game.id,
        new_values=data.model_dump(),
    )
    await publish_event("game_created", {"game_id": game.id, "tournament_id": data.tournament_id})

    return game


async def update_game_result(
    db: AsyncSession,
    game_id: int,
    data: GameResult,
    user_id: int | None = None,
) -> Game | None:
    """Update game result."""
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalar_one_or_none()
    if not game:
        return None

    old_result = game.result
    game.result = data.result
    await db.flush()
    await db.refresh(game)

    await log_activity(
        db, user_id, "update", "game", game_id,
        old_values={"result": old_result},
        new_values={"result": data.result},
    )
    await publish_event("game_result_updated", {"game_id": game_id, "result": data.result})

    return game


async def delete_game(
    db: AsyncSession,
    game_id: int,
    user_id: int | None = None,
) -> bool:
    """Delete a game by ID."""
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalar_one_or_none()
    if not game:
        return False

    old_values = {"tournament_id": game.tournament_id, "result": game.result}

    await db.delete(game)
    await db.flush()

    await log_activity(
        db, user_id, "delete", "game", game_id,
        old_values=old_values,
    )

    return True
