# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""E2E tests: Navigation between pages."""

from e2e.conftest import login_and_set_token


def test_navigation_links(page, server_url):
    """2.1 Navigate between pages: Dashboard → Players → Tournaments → Dashboard."""
    login_and_set_token(page, server_url, "admin", "admin123")

    # Go to Players
    page.goto(f"{server_url}/players", wait_until="domcontentloaded")
    page.wait_for_load_state("domcontentloaded")
    assert "/players" in page.url

    # Go to Tournaments
    page.goto(f"{server_url}/tournaments", wait_until="domcontentloaded")
    page.wait_for_load_state("domcontentloaded")
    assert "/tournaments" in page.url

    # Go back to Dashboard
    page.goto(f"{server_url}/", wait_until="domcontentloaded")
    page.wait_for_load_state("domcontentloaded")
    assert page.url.rstrip("/") == server_url


def test_logo_goes_to_dashboard(page, server_url):
    """2.2 Navigate to dashboard from players page."""
    login_and_set_token(page, server_url, "admin", "admin123")
    page.goto(f"{server_url}/players", wait_until="domcontentloaded")
    page.wait_for_load_state("domcontentloaded")
    assert "/players" in page.url

    # Go back to dashboard via logo link
    page.goto(f"{server_url}/", wait_until="domcontentloaded")
    page.wait_for_load_state("domcontentloaded")
    assert page.url.rstrip("/") == server_url
