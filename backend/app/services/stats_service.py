# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Stats service — head-to-head, top-rated, overall stats."""

from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Game, Player


async def get_head_to_head(
    db: AsyncSession,
    player1_id: int,
    player2_id: int,
) -> dict:
    """Get head-to-head statistics between two players."""
    pair_filter = or_(
        (Game.white_player_id == player1_id) & (Game.black_player_id == player2_id),
        (Game.white_player_id == player2_id) & (Game.black_player_id == player1_id),
    )

    query = select(
        func.count(Game.id).label("total_games"),
        # player1 wins: (white and 1-0) or (black and 0-1)
        func.count(case(
            ((Game.white_player_id == player1_id) & (Game.result == "1-0"), 1),
            ((Game.black_player_id == player1_id) & (Game.result == "0-1"), 1),
        )).label("player1_wins"),
        # player2 wins: (white and 0-1) or (black and 1-0)
        func.count(case(
            ((Game.white_player_id == player2_id) & (Game.result == "1-0"), 1),
            ((Game.black_player_id == player2_id) & (Game.result == "0-1"), 1),
        )).label("player2_wins"),
        func.count(case(
            (Game.result == "½-½", 1),
        )).label("draws"),
    ).where(pair_filter).where(Game.result.isnot(None))

    result = await db.execute(query)
    row = result.one()

    return {
        "player1_id": player1_id,
        "player2_id": player2_id,
        "total_games": row.total_games,
        "player1_wins": row.player1_wins,
        "player2_wins": row.player2_wins,
        "draws": row.draws,
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
    player_filter = or_(
        Game.white_player_id == player_id,
        Game.black_player_id == player_id,
    )

    query = select(
        func.count(Game.id).label("total_games"),
        # wins: (white and 1-0) or (black and 0-1)
        func.count(case(
            ((Game.white_player_id == player_id) & (Game.result == "1-0"), 1),
            ((Game.black_player_id == player_id) & (Game.result == "0-1"), 1),
        )).label("wins"),
        # losses: (white and 0-1) or (black and 1-0)
        func.count(case(
            ((Game.white_player_id == player_id) & (Game.result == "0-1"), 1),
            ((Game.black_player_id == player_id) & (Game.result == "1-0"), 1),
        )).label("losses"),
        func.count(case(
            (Game.result == "½-½", 1),
        )).label("draws"),
    ).where(player_filter).where(Game.result.isnot(None))

    result = await db.execute(query)
    row = result.one()

    total = row.total_games
    return {
        "player_id": player_id,
        "total_games": total,
        "wins": row.wins,
        "losses": row.losses,
        "draws": row.draws,
        "win_rate": round(row.wins / total * 100, 1) if total else 0.0,
    }
