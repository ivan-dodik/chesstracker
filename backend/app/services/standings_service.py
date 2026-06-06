"""Standings service — shared logic for calculating tournament standings.

Extracted from tournament_service and export_service to eliminate duplication.
"""

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Game, Player


async def calculate_standings(
    db: AsyncSession,
    tournament_id: int,
) -> list[dict]:
    """Calculate tournament standings with points, wins, draws, losses.

    Returns a list of dicts sorted by points descending, then player name.
    Each dict contains: player_id, player_name, points, games_played, wins, draws, losses.
    """
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
        player_result = await db.execute(select(Player).where(Player.id == pid))
        player = player_result.scalar_one_or_none()
        if player:
            standings.append({
                "player_id": pid,
                "player_name": player.name,
                "rating": player.rating,
                "points": points.get(pid, 0.0),
                "games_played": games_played.get(pid, 0),
                "wins": wins.get(pid, 0),
                "draws": draws.get(pid, 0),
                "losses": losses.get(pid, 0),
            })

    # Sort by points descending, then player name
    standings.sort(key=lambda x: (-x["points"], x["player_name"]))
    return standings
