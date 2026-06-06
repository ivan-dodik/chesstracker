"""Stats service — head-to-head, top-rated, overall stats."""

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Game, Player


async def get_head_to_head(
    db: AsyncSession,
    player1_id: int,
    player2_id: int,
) -> dict:
    """Get head-to-head statistics between two players."""
    query = select(Game).where(
        or_(
            (Game.white_player_id == player1_id) & (Game.black_player_id == player2_id),
            (Game.white_player_id == player2_id) & (Game.black_player_id == player1_id),
        )
    ).where(Game.result.isnot(None))

    result = await db.execute(query)
    games = list(result.scalars().all())

    player1_wins = 0
    player2_wins = 0
    draws = 0

    for game in games:
        if game.result == "1-0":
            if game.white_player_id == player1_id:
                player1_wins += 1
            else:
                player2_wins += 1
        elif game.result == "0-1":
            if game.white_player_id == player1_id:
                player2_wins += 1
            else:
                player1_wins += 1
        else:  # ½-½
            draws += 1

    return {
        "player1_id": player1_id,
        "player2_id": player2_id,
        "total_games": len(games),
        "player1_wins": player1_wins,
        "player2_wins": player2_wins,
        "draws": draws,
    }


async def get_top_rated(
    db: AsyncSession,
    limit: int = 10,
) -> list[Player]:
    """Get top-rated players."""
    query = select(Player).order_by(Player.rating.desc()).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_overall_stats(
    db: AsyncSession,
    player_id: int,
) -> dict:
    """Get overall statistics for a player."""
    query = select(Game).where(
        or_(
            Game.white_player_id == player_id,
            Game.black_player_id == player_id,
        )
    ).where(Game.result.isnot(None))

    result = await db.execute(query)
    games = list(result.scalars().all())

    wins = 0
    losses = 0
    draws = 0

    for game in games:
        if game.result == "1-0":
            if game.white_player_id == player_id:
                wins += 1
            else:
                losses += 1
        elif game.result == "0-1":
            if game.white_player_id == player_id:
                losses += 1
            else:
                wins += 1
        else:  # ½-½
            draws += 1

    return {
        "player_id": player_id,
        "total_games": len(games),
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "win_rate": round(wins / len(games) * 100, 1) if games else 0.0,
    }