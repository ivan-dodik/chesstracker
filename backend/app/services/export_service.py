# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Export service — CSV export for tournament standings."""

import csv
import io

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Tournament
from app.services.standings_service import calculate_standings


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

    # Use shared standings calculation
    standings = await calculate_standings(db, tournament_id)

    # Generate CSV
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["player_id", "player_name", "rating", "points", "games_played", "wins", "draws", "losses"],
    )
    writer.writeheader()
    writer.writerows(standings)

    csv_content = output.getvalue()
    output.close()

    return csv_content
