# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Import service — CSV import for tournament results."""

import csv
import io
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Game, Player, Tournament


def parse_result(result_str: str) -> str | None:
    """Parse a result string to standard format."""
    result_str = result_str.strip()
    if result_str in ("1-0", "1:0", "1"):
        return "1-0"
    if result_str in ("0-1", "0:1", "0"):
        return "0-1"
    if result_str in ("½-½", "1/2-1/2", "0.5-0.5", "0,5-0,5", "=", "draw", "½:½"):
        return "½-½"
    return None


async def import_tournament_csv(
    db: AsyncSession,
    tournament_id: int,
    csv_content: str,
) -> dict[str, Any]:
    """Import tournament results from CSV content.

    Expected CSV columns: round, white_player, black_player, result (or player, round, opponent, result)
    Returns summary of imported games.
    """
    # Verify tournament exists
    result = await db.execute(select(Tournament).where(Tournament.id == tournament_id))
    tournament = result.scalar_one_or_none()
    if not tournament:
        return {"success": False, "error": "Tournament not found"}

    reader = csv.DictReader(io.StringIO(csv_content))
    rows = list(reader)

    if not rows:
        return {"success": False, "error": "CSV is empty"}

    # Detect column format
    columns = rows[0].keys()
    has_player_format = "player" in columns

    if not (has_player_format or "white_player" in columns):
        return {
            "success": False,
            "error": "Expected columns: round, white_player, black_player, result OR round, player, opponent, result",
        }

    games_created = 0
    games_skipped = 0
    errors: list[str] = []

    for row_idx, row in enumerate(rows, start=2):
        try:
            round_num = int(row.get("round", "").strip())

            if has_player_format:
                # Format: round, player, opponent, result
                player_name = row.get("player", "").strip()
                opponent_name = row.get("opponent", "").strip()
                is_white = row.get("color", "").strip().lower() == "white"

                # Find players
                player = await _find_player(db, player_name)
                opponent = await _find_player(db, opponent_name)

                if not player or not opponent:
                    errors.append(f"Row {row_idx}: Player not found: {player_name or opponent_name}")
                    games_skipped += 1
                    continue

                white_id = player.id if is_white else opponent.id
                black_id = opponent.id if is_white else player.id
            else:
                # Format: round, white_player, black_player, result
                white_name = row.get("white_player", "").strip()
                black_name = row.get("black_player", "").strip()

                white_player = await _find_player(db, white_name)
                black_player = await _find_player(db, black_name)

                if not white_player or not black_player:
                    errors.append(f"Row {row_idx}: Player not found: {white_name or black_name}")
                    games_skipped += 1
                    continue

                white_id = white_player.id
                black_id = black_player.id

            # Parse result
            result_value = parse_result(row.get("result", ""))
            if result_value is None:
                errors.append(f"Row {row_idx}: Invalid result format: {row.get('result', '')}")
                games_skipped += 1
                continue

            # Check if game already exists
            existing = await db.execute(
                select(Game).where(
                    Game.tournament_id == tournament_id,
                    Game.game_round == round_num,
                    Game.white_player_id == white_id,
                    Game.black_player_id == black_id,
                )
            )
            if existing.scalar_one_or_none():
                games_skipped += 1
                continue

            game = Game(
                tournament_id=tournament_id,
                game_round=round_num,
                white_player_id=white_id,
                black_player_id=black_id,
                result=result_value,
            )
            db.add(game)
            await db.flush()
            games_created += 1

        except (ValueError, KeyError) as e:
            errors.append(f"Row {row_idx}: {e!s}")
            games_skipped += 1

    return {
        "success": True,
        "games_created": games_created,
        "games_skipped": games_skipped,
        "errors": errors,
    }


async def _find_player(db: AsyncSession, name: str) -> Player | None:
    """Find a player by exact name match."""
    if not name:
        return None
    result = await db.execute(select(Player).where(Player.name == name))
    return result.scalar_one_or_none()
