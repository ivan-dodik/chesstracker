# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""E2E tests: SSE Alpine.js refresh — verify custom DOM event pattern works.

The SSE callback dispatches custom events (sse:refresh-tournament, sse:refresh-player),
and Alpine templates listen via @sse:refresh-*.window to call their data methods.
This avoids depending on Alpine.js internals (_x_dataStack).
"""

import os


def _read(path: str) -> str:
    with open(path) as f:
        return f.read()


def test_tournament_detail_has_custom_event_handler():
    """Tournament detail template listens for sse:refresh-tournament custom event."""
    content = _read(os.path.join(
        os.path.dirname(__file__), "..", "app", "templates", "tournaments", "detail.html",
    ))
    assert "@sse:refresh-tournament.window" in content, (
        "Tournament detail must use @sse:refresh-tournament.window for SSE refresh"
    )
    assert "loadStandings" in content
    assert "loadGames" in content


def test_player_detail_has_custom_event_handler():
    """Player detail template listens for sse:refresh-player custom event."""
    content = _read(os.path.join(
        os.path.dirname(__file__), "..", "app", "templates", "players", "detail.html",
    ))
    assert "@sse:refresh-player.window" in content, (
        "Player detail must use @sse:refresh-player.window for SSE refresh"
    )
    assert "refreshAll" in content, "Player detail must have refreshAll() method"


def test_tournament_sse_dispatches_custom_event():
    """Tournament detail SSE script dispatches sse:refresh-tournament custom event."""
    content = _read(os.path.join(
        os.path.dirname(__file__), "..", "app", "templates", "tournaments", "detail.html",
    ))
    assert "sse:refresh-tournament" in content
    assert "CustomEvent" in content
    assert "dispatchEvent" in content


def test_player_sse_dispatches_custom_event():
    """Player detail SSE script dispatches sse:refresh-player custom event."""
    content = _read(os.path.join(
        os.path.dirname(__file__), "..", "app", "templates", "players", "detail.html",
    ))
    assert "sse:refresh-player" in content
    assert "CustomEvent" in content
    assert "dispatchEvent" in content


def test_no_alpine_internals_in_templates():
    """Templates must NOT use Alpine.js internals (_x_dataStack, __x)."""
    for template_path in [
        os.path.join(os.path.dirname(__file__), "..", "app", "templates", "tournaments", "detail.html"),
        os.path.join(os.path.dirname(__file__), "..", "app", "templates", "players", "detail.html"),
    ]:
        content = _read(template_path)
        assert "_x_dataStack" not in content, f"{template_path} must not use _x_dataStack"
        assert "el.__x" not in content, f"{template_path} must not use el.__x"
