# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Game service — business logic for game CRUD."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Game, Player
from app.schemas.game import GameCreate, GameResult
from app.services.activity_log_service import log_activity
from app.services.rating_calculation_service import update_ratings_after_game
from app.services.sse_events import SSEEvents
from app.services.sse_service import publish_event


async def get_game_by_id(
    db: AsyncSession,
    game_id: int,
) -> dict | None:
    """Get a single game by ID with player names."""
    query = (
        select(Game)
        .options(
            selectinload(Game.white_player),
            selectinload(Game.black_player),
        )
        .where(Game.id == game_id)
    )
    result = await db.execute(query)
    game = result.scalar_one_or_none()
    if not game:
        return None
    return {
        "id": game.id,
        "tournament_id": game.tournament_id,
        "game_round": game.game_round,
        "white_player_id": game.white_player_id,
        "black_player_id": game.black_player_id,
        "white_player_name": game.white_player.name if game.white_player else None,
        "black_player_name": game.black_player.name if game.black_player else None,
        "result": game.result,
        "played_at": game.played_at,
        "created_at": game.created_at,
    }


async def get_games_by_tournament(
    db: AsyncSession,
    tournament_id: int,
    page: int = 1,
    per_page: int = 50,
) -> tuple[list[dict], int]:
    """Get paginated list of games for a tournament with player names."""
    count_query = select(func.count(Game.id)).where(Game.tournament_id == tournament_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Use joined loading to avoid N+1 queries for player names
    query = (
        select(Game)
        .options(
            # Eagerly load related players
            selectinload(Game.white_player),
            selectinload(Game.black_player),
        )
        .where(Game.tournament_id == tournament_id)
        .order_by(Game.game_round, Game.id)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(query)
    games = list(result.scalars().all())

    # Enrich with player names (no extra queries needed)
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

    # Calculate ratings if result is provided
    if game.result:
        await update_ratings_after_game(db, game, user_id=user_id)

    # Enrich SSE event with player names
    white_name = None
    black_name = None
    try:
        w = await db.execute(select(Player).where(Player.id == game.white_player_id))
        wp = w.scalar_one_or_none()
        if wp:
            white_name = wp.name
        b = await db.execute(select(Player).where(Player.id == game.black_player_id))
        bp = b.scalar_one_or_none()
        if bp:
            black_name = bp.name
    except Exception:
        pass

    await publish_event(SSEEvents.GAME_CREATED, {
        "game_id": game.id,
        "tournament_id": data.tournament_id,
        "result": game.result,
        "white_player_name": white_name,
        "black_player_name": black_name,
    })

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

    # Recalculate ratings if result changed
    if data.result and data.result != old_result:
        await update_ratings_after_game(db, game, user_id=user_id)

    # Enrich SSE event with player names
    white_name = None
    black_name = None
    try:
        w = await db.execute(select(Player).where(Player.id == game.white_player_id))
        wp = w.scalar_one_or_none()
        if wp:
            white_name = wp.name
        b = await db.execute(select(Player).where(Player.id == game.black_player_id))
        bp = b.scalar_one_or_none()
        if bp:
            black_name = bp.name
    except Exception:
        pass

    await publish_event(SSEEvents.GAME_UPDATED, {
        "game_id": game_id,
        "result": data.result,
        "white_player_name": white_name,
        "black_player_name": black_name,
    })

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

    await publish_event(SSEEvents.GAME_DELETED, {
        "game_id": game_id,
        "tournament_id": old_values["tournament_id"],
    })

    return True
