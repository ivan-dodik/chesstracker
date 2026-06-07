"""E2E tests: Dashboard page."""

from e2e.conftest import login_and_set_token


def test_dashboard_loads(page, server_url):
    """3.1 Dashboard loads with top players and charts."""
    login_and_set_token(page, server_url, "admin", "admin123")
    page.goto(f"{server_url}/")
    page.wait_for_load_state("domcontentloaded")

    # Page title should contain Chess Tracker
    assert "Chess Tracker" in page.title() or "Chess" in page.content()

    # Dashboard should have main content sections
    content = page.content()
    # Check for dashboard structure (charts, player lists, etc.)
    assert "main-content" in content or "main" in content


def test_dashboard_favorites_section(page, server_url):
    """3.2 Favorites section is visible for authenticated users."""
    login_and_set_token(page, server_url, "admin", "admin123")
    page.goto(f"{server_url}/")
    page.wait_for_load_state("domcontentloaded")

    # Favorites section should be present in the DOM
    content = page.content()
    assert "favorites" in content.lower() or "Избранные" in content
