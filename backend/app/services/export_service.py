"""Export service — CSV export for tournament standings."""

import csv
import io

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Game, Player, Tournament


async def export_tournament_csv(
    db: AsyncSession,
    tournament_id: int,
) -> str | None:
    """Export tournament standings as CSV string."""
    # Verify tournament exists
    result = await db.execute(select(Tournament).where(Tournament.id == tournament_id))
    tournament = result.scalar_one_or_none()
    if not tournament:
        return None

    # Get all games for the tournament
    games_result = await db.execute(
        select(Game).where(Game.tournament_id == tournament_id)
    )
    games = list(games_result.scalars().all())

    # Get all unique player IDs from games
    player_ids: set[int] = set()
    for game in games:
        player_ids.add(game.white_player_id)
        player_ids.add(game.black_player_id)

    # Get player info
    players_result = await db.execute(
        select(Player).where(Player.id.in_(player_ids))
    )
    players = {p.id: p for p in players_result.scalars().all()}

    # Calculate points for each player
    points: dict[int, float] = {}
    for game in games:
        if game.result:
            if game.result == "1-0":
                points[game.white_player_id] = points.get(game.white_player_id, 0) + 1
            elif game.result == "0-1":
                points[game.black_player_id] = points.get(game.black_player_id, 0) + 1
            else:  # ½-½
                points[game.white_player_id] = points.get(game.white_player_id, 0) + 0.5
                points[game.black_player_id] = points.get(game.black_player_id, 0) + 0.5

    # Build standings
    standings = []
    for pid in sorted(player_ids, key=lambda p: points.get(p, 0), reverse=True):
        player = players.get(pid)
        if player:
            standings.append({
                "player_id": pid,
                "player_name": player.name,
                "rating": player.rating,
                "points": points.get(pid, 0),
            })

    # Generate CSV
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["player_id", "player_name", "rating", "points"],
    )
    writer.writeheader()
    writer.writerows(standings)

    csv_content = output.getvalue()
    output.close()

    return csv_content
