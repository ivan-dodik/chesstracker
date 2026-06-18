# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""E2E tests: M21 — Doughnut chart on player detail page."""

import os


def _read(path: str) -> str:
    with open(path) as f:
        return f.read()


def test_player_detail_has_canvas():
    """M21.1 Player detail template has canvas element for Chart.js."""
    content = _read(
        os.path.join(os.path.dirname(__file__), "..", "app", "templates", "players", "detail.html")
    )
    assert "<canvas" in content, "Player detail should have canvas element for charts"


def test_player_detail_has_doughnut_section():
    """M21.2 Player detail template has results distribution chart section."""
    content = _read(
        os.path.join(os.path.dirname(__file__), "..", "app", "templates", "players", "detail.html")
    )
    has_section = any(
        kw in content
        for kw in [
            "Распределение результатов",
            "resultsChart",
            "overallStats",
            "doughnut",
            "wins",
            "losses",
            "draws",
        ]
    )
    assert has_section, "Player detail should have results distribution section"


def test_player_detail_has_chart_js_import():
    """M21.3 Player detail template uses Chart.js."""
    content = _read(
        os.path.join(os.path.dirname(__file__), "..", "app", "templates", "players", "detail.html")
    )
    has_chart = any(kw in content for kw in ["Chart", "chart.js", "chartjs", "Chart.js"])
    assert has_chart, "Player detail should use Chart.js for doughnut chart"
