"""Game service — business logic for game CRUD."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Game
from app.schemas.game import GameCreate, GameResult


async def get_games_by_tournament(
    db: AsyncSession,
    tournament_id: int,
    page: int = 1,
    per_page: int = 50,
) -> tuple[list[Game], int]:
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

    return games, total


async def create_game(db: AsyncSession, data: GameCreate) -> Game:
    """Create a new game."""
    game = Game(**data.model_dump())
    db.add(game)
    await db.flush()
    await db.refresh(game)
    return game


async def update_game_result(db: AsyncSession, game_id: int, data: GameResult) -> Game | None:
    """Update game result."""
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalar_one_or_none()
    if not game:
        return None
    game.result = data.result
    await db.flush()
    await db.refresh(game)
    return game


async def delete_game(db: AsyncSession, game_id: int) -> bool:
    """Delete a game by ID."""
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalar_one_or_none()
    if not game:
        return False
    await db.delete(game)
    await db.flush()
    return True