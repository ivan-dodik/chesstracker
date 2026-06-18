# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Unit tests for rating calculation service (ELO)."""

import pytest

from app.services.rating_calculation_service import calculate_elo_rating


class TestEloCalculation:
    """Test ELO rating calculation."""

    def test_white_win_higher_rated(self):
        """White wins against higher-rated opponent — rating increases significantly."""
        new_rating = calculate_elo_rating(1500, 1700, "1-0")
        assert new_rating > 1500

    def test_white_win_lower_rated(self):
        """White wins against lower-rated opponent — small increase."""
        new_rating = calculate_elo_rating(1700, 1500, "1-0")
        assert new_rating > 1700
        # Gain should be smaller than beating a higher-rated player
        big_gain = calculate_elo_rating(1500, 1700, "1-0") - 1500
        small_gain = new_rating - 1700
        assert big_gain > small_gain

    def test_black_win(self):
        """Black wins (0-1 from white's perspective = loss for white)."""
        new_rating = calculate_elo_rating(1500, 1500, "0-1")
        assert new_rating < 1500

    def test_draw_equal_ratings(self):
        """Draw between equal-rated players — no change."""
        new_rating = calculate_elo_rating(1500, 1500, "½-½")
        assert new_rating == 1500

    def test_draw_unequal_ratings(self):
        """Draw: stronger player loses rating, weaker gains."""
        strong = calculate_elo_rating(1700, 1500, "½-½")
        weak = calculate_elo_rating(1500, 1700, "½-½")
        assert strong < 1700
        assert weak > 1500

    def test_minimum_rating(self):
        """Rating never drops below 100."""
        new_rating = calculate_elo_rating(100, 3000, "0-1")
        assert new_rating >= 100

    def test_custom_k_factor(self):
        """Higher K-factor = bigger rating changes."""
        k16 = calculate_elo_rating(1500, 1500, "1-0", k_factor=16)
        k32 = calculate_elo_rating(1500, 1500, "1-0", k_factor=32)
        assert k32 > k16

    def test_unknown_result(self):
        """Unknown result returns same rating."""
        new_rating = calculate_elo_rating(1500, 1500, "???")
        assert new_rating == 1500

    def test_symmetry(self):
        """If white wins, the rating change is symmetric to black winning."""
        white_win = calculate_elo_rating(1500, 1500, "1-0")
        black_win = calculate_elo_rating(1500, 1500, "0-1")
        assert white_win + black_win == 3000  # Sum preserved