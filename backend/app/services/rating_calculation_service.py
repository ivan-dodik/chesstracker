# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Rating calculation service — ELO rating system."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Game, Player, RatingHistory
from app.services.activity_log_service import log_activity
from app.services.sse_service import publish_event


def calculate_elo_rating(
    player_rating: int,
    opponent_rating: int,
    result: str,
    k_factor: int = 32,
) -> int:
    """Calculate new ELO rating.

    Args:
        player_rating: Current rating of the player.
        opponent_rating: Current rating of the opponent.
        result: Game result from player's perspective.
            "1-0" = player wins (white), "0-1" = player wins (black),
            "½-½" = draw.
        k_factor: K-factor (default 32).

    Returns:
        New rating (integer, minimum 100).
    """
    # Expected score
    expected = 1 / (1 + 10 ** ((opponent_rating - player_rating) / 400))

    # Actual score
    if result == "1-0":
        actual = 1.0  # White wins
    elif result == "0-1":
        actual = 0.0  # Black wins
    elif result == "½-½":
        actual = 0.5  # Draw
    else:
        return player_rating  # Unknown result, no change

    new_rating = player_rating + k_factor * (actual - expected)
    return max(100, int(round(new_rating)))


async def update_ratings_after_game(
    db: AsyncSession,
    game: Game,
) -> None:
    """Update player ratings and create RatingHistory after a game.

    Only updates if the game has a result.
    """
    if not game.result:
        return

    # Load players
    white_result = await db.execute(
        select(Player).where(Player.id == game.white_player_id)
    )
    white = white_result.scalar_one_or_none()
    black_result = await db.execute(
        select(Player).where(Player.id == game.black_player_id)
    )
    black = black_result.scalar_one_or_none()

    if not white or not black:
        return

    old_white_rating = white.rating
    old_black_rating = black.rating

    # Calculate new ratings
    # White perspective: "1-0" = win, "0-1" = loss, "½-½" = draw
    new_white_rating = calculate_elo_rating(
        old_white_rating, old_black_rating, game.result
    )
    # Black perspective: "1-0" = loss, "0-1" = win, "½-½" = draw
    if game.result == "1-0":
        black_result_str = "0-1"
    elif game.result == "0-1":
        black_result_str = "1-0"
    else:
        black_result_str = "½-½"
    new_black_rating = calculate_elo_rating(
        old_black_rating, old_white_rating, black_result_str
    )

    # Update ratings
    white.rating = new_white_rating
    black.rating = new_black_rating
    await db.flush()

    now = datetime.now(UTC)

    # Create RatingHistory entries
    white_history = RatingHistory(
        player_id=white.id,
        rating=new_white_rating,
        date=now,
        tournament_id=game.tournament_id,
    )
    black_history = RatingHistory(
        player_id=black.id,
        rating=new_black_rating,
        date=now,
        tournament_id=game.tournament_id,
    )
    db.add(white_history)
    db.add(black_history)
    await db.flush()

    # Log rating changes
    if new_white_rating != old_white_rating:
        await log_activity(
            db, None, "update", "rating", white.id,
            old_values={"rating": old_white_rating, "player_name": white.name},
            new_values={
                "rating": new_white_rating,
                "change": new_white_rating - old_white_rating,
                "tournament_id": game.tournament_id,
            },
        )
    if new_black_rating != old_black_rating:
        await log_activity(
            db, None, "update", "rating", black.id,
            old_values={"rating": old_black_rating, "player_name": black.name},
            new_values={
                "rating": new_black_rating,
                "change": new_black_rating - old_black_rating,
                "tournament_id": game.tournament_id,
            },
        )

    # Publish SSE events
    if new_white_rating != old_white_rating:
        await publish_event("rating_updated", {
            "player_id": white.id,
            "player_name": white.name,
            "old_rating": old_white_rating,
            "new_rating": new_white_rating,
        })
    if new_black_rating != old_black_rating:
        await publish_event("rating_updated", {
            "player_id": black.id,
            "player_name": black.name,
            "old_rating": old_black_rating,
            "new_rating": new_black_rating,
        })


async def recalculate_all_ratings(
    db: AsyncSession,
    tournament_id: int,
) -> None:
    """Recalculate all ratings for a tournament's games.

    Used for bulk import or recalculation.
    """
    query = (
        select(Game)
        .where(Game.tournament_id == tournament_id)
        .where(Game.result.isnot(None))
        .order_by(Game.id)
    )
    result = await db.execute(query)
    games = list(result.scalars().all())

    # Reset all player ratings in this tournament to initial values
    # (This is a simplified approach — full recalc would need initial ratings)
    for game in games:
        await update_ratings_after_game(db, game)
