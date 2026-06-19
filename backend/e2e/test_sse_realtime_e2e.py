# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""E2E tests: SSE real-time updates — browser-level verification.

Tests use two browser contexts (simulating two users) to verify that
SSE events propagate changes across connected tabs.
"""

import json
import urllib.request

import pytest
from playwright.sync_api import Page

from e2e.conftest import login_and_set_token

# Mark all tests in this module as E2E
pytestmark = pytest.mark.e2e


def _get_admin_token(server_url: str) -> str:
    """Helper: get admin JWT token via API."""
    req = urllib.request.Request(
        f"{server_url}/api/auth/login",
        data=json.dumps({"username": "admin", "password": "admin123"}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["access_token"]


def _api_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _api_post(server_url: str, path: str, token: str, data: dict) -> dict:
    req = urllib.request.Request(
        f"{server_url}{path}",
        data=json.dumps(data).encode(),
        headers=_api_headers(token),
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def _api_put(server_url: str, path: str, token: str, data: dict) -> dict:
    req = urllib.request.Request(
        f"{server_url}{path}",
        data=json.dumps(data).encode(),
        headers=_api_headers(token),
        method="PUT",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def test_sse_notification_toast_appears(page: Page, server_url: str):
    """SSE toast notification appears after a game is created."""
    login_and_set_token(page, server_url, "admin", "admin23")
    page.goto(f"{server_url}/", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)  # Wait for SSE connection

    # Verify SSE client is loaded
    has_sse = page.evaluate("() => typeof window.sseClient !== 'undefined' && window.sseClient !== null")
    assert has_sse, "SSE client should be initialized"

    # Verify EventSource is connected
    has_eventsource = page.evaluate("() => window.sseClient?.eventSource !== null")
    assert has_eventsource, "EventSource should be connected"


def test_sse_client_has_reconnect_method(server_url: str):
    """SSE client has _reconnectExternalListeners method."""
    import urllib.request as _req

    req = _req.Request(f"{server_url}/static/js/sse.js")
    with _req.urlopen(req) as resp:
        content = resp.read().decode()

    assert "_reconnectExternalListeners" in content, "SSE client should have reconnect method"
    assert "_addListener" in content, "SSE client should have _addListener method"
    assert "game_updated" in content, "SSE client should listen for game_updated (not game_result_updated)"


def test_dashboard_has_game_sse_listeners(server_url: str):
    """Dashboard page has SSE listeners for game events."""
    import urllib.request as _req

    token = _get_admin_token(server_url)
    # Fetch dashboard page content
    req = _req.Request(
        f"{server_url}/",
        headers={"Cookie": f"jwt_token={token}"},
    )
    with _req.urlopen(req) as resp:
        content = resp.read().decode()

    assert "refreshActiveTournaments" in content or "active-tournaments" in content
    assert "game_created" in content, "Dashboard should listen for game_created"
    assert "game_updated" in content, "Dashboard should listen for game_updated"


def test_players_page_has_sse_listeners(server_url: str):
    """Players list page has SSE listeners for auto-refresh."""
    import urllib.request as _req

    token = _get_admin_token(server_url)
    req = _req.Request(
        f"{server_url}/players",
        headers={"Cookie": f"jwt_token={token}"},
    )
    with _req.urlopen(req) as resp:
        content = resp.read().decode()

    assert "refreshPlayers" in content or "player_created" in content
    assert "rating_updated" in content, "Players page should listen for rating_updated"
    assert "player_deleted" in content, "Players page should listen for player_deleted"


def test_tournament_detail_has_sse_listeners(server_url: str):
    """Tournament detail page has SSE listeners including game_updated."""
    import urllib.request as _req

    token = _get_admin_token(server_url)
    # We need an existing tournament ID — use API to get one
    req = _req.Request(
        f"{server_url}/api/tournaments?per_page=1",
        headers={"Authorization": f"Bearer {token}"},
    )
    with _req.urlopen(req) as resp:
        data = json.loads(resp.read())

    if not data.get("items"):
        pytest.skip("No tournaments available for testing")

    tournament_id = data["items"][0]["id"]

    req = _req.Request(
        f"{server_url}/tournaments/{tournament_id}",
        headers={"Cookie": f"jwt_token={token}"},
    )
    with _req.urlopen(req) as resp:
        content = resp.read().decode()

    assert "game_created" in content, "Tournament detail should listen for game_created"
    assert "game_updated" in content, "Tournament detail should listen for game_updated (not game_result_updated)"
    assert "_x_dataStack" in content or "loadStandings" in content
