# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""E2E tests: SSE chart survival — doughnut chart persists after SSE refresh.

The core bug: Alpine's x-if destroys/recreates DOM on data change, which kills
the Chart.js canvas. The fix uses x-show instead, so the canvas survives.
"""

import os


def _read(path: str) -> str:
    with open(path) as f:
        return f.read()


TEMPLATE = os.path.join(
    os.path.dirname(__file__), "..", "app", "templates", "players", "detail.html",
)


def test_player_detail_uses_x_show_not_x_if():
    """Player content container uses x-show (not x-if) to preserve canvas DOM."""
    content = _read(TEMPLATE)
    # The main player content div should use x-show, not x-if
    assert 'x-show="player"' in content, (
        "Player detail must use x-show=\"player\" to avoid destroying canvas on re-render"
    )
    # There should NOT be a <template x-if="player"> wrapping the charts
    assert "<template x-if=\"player\">" not in content, (
        "Player detail must NOT use <template x-if=\"player\"> — it destroys canvas"
    )


def test_refresh_all_does_not_call_load_player():
    """refreshAll() must NOT call loadPlayer() to avoid triggering x-if re-render."""
    content = _read(TEMPLATE)
    # Find the refreshAll function body
    idx = content.find("async refreshAll()")
    assert idx != -1, "refreshAll() method must exist"
    # Get the function body (until next method or closing brace)
    body_end = content.find("renderResultsChart()", idx)
    body = content[idx:body_end]
    assert "this.loadPlayer" not in body, (
        "refreshAll() must NOT call this.loadPlayer() — it triggers unnecessary DOM re-render"
    )


def test_refresh_all_has_no_settimeout():
    """refreshAll() should not need setTimeout — x-show preserves DOM."""
    content = _read(TEMPLATE)
    idx = content.find("async refreshAll()")
    assert idx != -1
    body_end = content.find("renderResultsChart()", idx)
    body = content[idx:body_end]
    assert "setTimeout" not in body, (
        "refreshAll() should not need setTimeout when using x-show"
    )


def test_chart_canvas_has_x_ref():
    """Chart canvas has x-ref for Alpine access."""
    content = _read(TEMPLATE)
    assert 'x-ref="resultsChart"' in content, "Doughnut chart canvas must have x-ref"
    assert 'x-ref="ratingChart"' in content, "Rating chart canvas must have x-ref"
