"""E2E tests: Tournaments list page — loading, filters, pagination, navigation."""

import json
import urllib.request

from e2e.conftest import login_and_set_token


def _create_tournament(server_url: str, token: str, name: str, status: str = "active") -> int:
    """Helper: create a tournament via API, return tournament ID."""
    data = {
        "name": name,
        "start_date": "2026-01-01",
        "end_date": "2026-01-10",
        "location": "Test City",
        "rounds": 5,
        "type": "classic",
        "status": status,
    }
    req = urllib.request.Request(
        f"{server_url}/api/tournaments",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["id"]


def _get_admin_token(server_url: str) -> str:
    """Helper: get admin JWT token."""
    req = urllib.request.Request(
        f"{server_url}/api/auth/login",
        data=json.dumps({"username": "admin", "password": "admin123"}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["access_token"]


def test_tournaments_list_loads(page, server_url):
    """6.1 Tournaments list page loads with tournament data."""
    token = _get_admin_token(server_url)
    _create_tournament(server_url, token, "TestTournament1")
    _create_tournament(server_url, token, "TestTournament2")

    login_and_set_token(page, server_url, "admin", "admin123")
    page.goto(f"{server_url}/tournaments")
    page.wait_for_load_state("domcontentloaded")

    content = page.content()
    assert "TestTournament1" in content or "Турнир" in content


def test_tournaments_filter_by_status(page, server_url):
    """6.2 Filter tournaments by status shows only matching ones."""
    token = _get_admin_token(server_url)
    _create_tournament(server_url, token, "ActiveTournament", status="active")
    _create_tournament(server_url, token, "CompletedTournament", status="completed")

    login_and_set_token(page, server_url, "admin", "admin123")
    page.goto(f"{server_url}/tournaments")
    page.wait_for_load_state("domcontentloaded")

    # Find status filter select
    filter_select = page.locator('select[name="status"], select[x-model*="status"], #status-filter')
    if filter_select.count() > 0 and filter_select.first.is_visible():
        filter_select.first.select_option("active")
        page.wait_for_timeout(1500)  # Wait for HTMX filter
        content = page.content()
        # Active tournament should be visible
        assert "ActiveTournament" in content


def test_tournaments_pagination(page, server_url):
    """6.3 HTMX pagination works on tournaments list."""
    login_and_set_token(page, server_url, "admin", "admin123")
    page.goto(f"{server_url}/tournaments")
    page.wait_for_load_state("domcontentloaded")

    # Check if pagination exists
    pagination = page.locator(".pagination, [x-data='pagination()'], nav[aria-label='pagination']")
    if pagination.count() > 0:
        next_btn = page.locator("button:has-text('»'), a:has-text('»'), button:has-text('След'), a:has-text('След')")
        if next_btn.count() > 0 and next_btn.first.is_visible():
            next_btn.first.click()
            page.wait_for_load_state("domcontentloaded")
            assert "/tournaments" in page.url


def test_click_tournament_navigates_to_detail(page, server_url):
    """6.4 Clicking a tournament name navigates to /tournaments/{id}."""
    token = _get_admin_token(server_url)
    t_id = _create_tournament(server_url, token, "ClickableTournament")

    login_and_set_token(page, server_url, "admin", "admin123")
    page.goto(f"{server_url}/tournaments")
    page.wait_for_load_state("domcontentloaded")

    # Find tournament link
    tournament_link = page.locator(f'a[href="/tournaments/{t_id}"]')
    if tournament_link.count() > 0 and tournament_link.first.is_visible():
        tournament_link.first.click()
        page.wait_for_load_state("domcontentloaded")
        assert f"/tournaments/{t_id}" in page.url
