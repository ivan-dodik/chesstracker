# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""E2E tests: Navigation between pages."""

from e2e.conftest import login_and_set_token


def test_navigation_links(page, server_url):
    """2.1 Click navigation links: Dashboard → Players → Tournaments."""
    login_and_set_token(page, server_url, "admin", "admin123")

    # Go to Players
    page.click('a[href="/players"]')
    page.wait_for_load_state("domcontentloaded")
    assert "/players" in page.url

    # Go to Tournaments
    page.click('a[href="/tournaments"]')
    page.wait_for_load_state("domcontentloaded")
    assert "/tournaments" in page.url

    # Go back to Dashboard
    page.click('a[href="/"]')
    page.wait_for_load_state("domcontentloaded")
    assert page.url.rstrip("/") == server_url


def test_logo_goes_to_dashboard(page, server_url):
    """2.2 Click logo from any page → redirect to /."""
    login_and_set_token(page, server_url, "admin", "admin123")
    page.goto(f"{server_url}/players")
    page.wait_for_load_state("domcontentloaded")

    # Click the logo
    page.click(".navbar-logo")
    page.wait_for_load_state("domcontentloaded")
    assert page.url.rstrip("/") == server_url
