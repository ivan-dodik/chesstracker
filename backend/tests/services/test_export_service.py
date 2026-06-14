# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Unit tests for export service.

Tests CSV export for tournament standings.
"""

import csv
import io

import pytest

from app.services.export_service import export_tournament_csv


@pytest.mark.asyncio
class TestExportService:
    """Tests for export service."""

    async def test_export_csv_success(self, db_session, sample_tournament, sample_player):
        """Test successful CSV export with standings data."""
        from app.models import Game, Player

        player2 = Player(name="Opponent", rating=1400, city="Lyon")
        db_session.add(player2)
        await db_session.flush()

        game = Game(
            tournament_id=sample_tournament.id, game_round=1,
            white_player_id=sample_player.id, black_player_id=player2.id,
            result="1-0",
        )
        db_session.add(game)
        await db_session.flush()

        csv_content = await export_tournament_csv(db_session, sample_tournament.id)
        assert csv_content is not None

        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)
        assert len(rows) == 2

        winner = [r for r in rows if r["player_name"] == "Test Player"][0]
        assert winner["points"] == "1.0"
        assert winner["wins"] == "1"
        assert winner["losses"] == "0"

    async def test_export_csv_empty_tournament(self, db_session, sample_tournament):
        """Test CSV export for a tournament with no games."""
        csv_content = await export_tournament_csv(db_session, sample_tournament.id)
        assert csv_content is not None

        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)
        assert len(rows) == 0

    async def test_export_csv_nonexistent_tournament(self, db_session):
        """Test CSV export for a nonexistent tournament."""
        csv_content = await export_tournament_csv(db_session, 99999)
        assert csv_content is None
