# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""E2E tests: SSE chart survival — ApexCharts donut persists after SSE refresh.

Uses ApexCharts with updateSeries() for reactive data updates.
No canvas destroy/create cycle needed.
"""

import os


def _read(path: str) -> str:
    with open(path) as f:
        return f.read()


TEMPLATE = os.path.join(
    os.path.dirname(__file__), "..", "app", "templates", "players", "detail.html",
)


def test_player_detail_uses_x_show_not_x_if():
    """Player content container uses x-show (not x-if) to preserve chart DOM."""
    content = _read(TEMPLATE)
    assert 'x-show="player"' in content, (
        "Player detail must use x-show=\"player\""
    )
    assert "<template x-if=\"player\">" not in content, (
        "Player detail must NOT use <template x-if=\"player\">"
    )


def test_refresh_all_does_not_call_load_player():
    """refreshAll() must NOT call loadPlayer()."""
    content = _read(TEMPLATE)
    idx = content.find("async refreshAll()")
    assert idx != -1, "refreshAll() method must exist"
    body_end = content.find("renderResultsChart()", idx)
    body = content[idx:body_end]
    assert "this.loadPlayer" not in body, (
        "refreshAll() must NOT call this.loadPlayer()"
    )


def test_uses_apexcharts_not_chartjs():
    """Template uses ApexCharts, not Chart.js."""
    content = _read(TEMPLATE)
    assert "ApexCharts" in content, "Must use ApexCharts"
    assert "new Chart(" not in content, "Must NOT use Chart.js"
    assert "new ApexCharts(" in content, "Must create ApexCharts instance"


def test_doughnut_uses_update_series():
    """Doughnut chart uses updateSeries() for reactive updates."""
    content = _read(TEMPLATE)
    idx = content.find("renderResultsChart() {")
    assert idx != -1, "renderResultsChart must exist"
    body = content[idx:idx+1200]
    assert "updateSeries" in body, "renderResultsChart must use updateSeries()"
    assert "chart: { type: 'donut'" in body or "type: 'donut'" in body, (
        "renderResultsChart must create donut chart"
    )


def test_line_chart_uses_update_series():
    """Line chart uses updateSeries() for reactive updates."""
    content = _read(TEMPLATE)
    idx = content.find("renderRatingChart() {")
    assert idx != -1, "renderRatingChart must exist"
    body = content[idx:idx+1500]
    assert "updateSeries" in body, "renderRatingChart must use updateSeries()"
    assert "type: 'line'" in body, "renderRatingChart must create line chart"


def test_chart_containers_are_divs():
    """ApexCharts uses div containers, not canvas elements."""
    content = _read(TEMPLATE)
    assert '<canvas' not in content.split('<script>')[0], (
        "ApexCharts uses <div>, not <canvas>"
    )


def test_x_cloak_on_player_container():
    """Player container uses x-cloak."""
    content = _read(TEMPLATE)
    assert 'x-cloak' in content, "Player detail must use x-cloak"


def test_player_properties_use_optional_chaining():
    """Player properties use optional chaining to avoid null errors on load."""
    content = _read(TEMPLATE)
    assert "player?.name" in content, "player.name must use optional chaining"
    assert "player?.rating" in content, "player.rating must use optional chaining"
    assert "player?.city" in content, "player.city must use optional chaining"
