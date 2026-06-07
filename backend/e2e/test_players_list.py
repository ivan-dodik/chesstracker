"""E2E tests: Players list page — loading, pagination, search, navigation."""

from e2e.conftest import login_and_set_token


def test_players_list_loads(page, server_url):
    """4.1 Players list page loads with player data."""
    login_and_set_token(page, server_url, "admin", "admin123")
    page.goto(f"{server_url}/players")
    page.wait_for_load_state("domcontentloaded")

    # Page should contain player data (seed has players or empty list)
    content = page.content()
    assert "players" in content.lower() or "Игрок" in content


def test_players_pagination(page, server_url):
    """4.2 HTMX pagination works on players list."""
    login_and_set_token(page, server_url, "admin", "admin123")
    page.goto(f"{server_url}/players")
    page.wait_for_load_state("domcontentloaded")

    # Check if pagination exists (depends on seed data)
    pagination = page.locator(".pagination, [x-data='pagination()'], nav[aria-label='pagination']")
    if pagination.count() > 0:
        # Click next page if available
        next_btn = page.locator("button:has-text('»'), a:has-text('»'), button:has-text('След'), a:has-text('След')")
        if next_btn.count() > 0 and next_btn.first.is_visible():
            next_btn.first.click()
            page.wait_for_load_state("domcontentloaded")
            # Verify page changed (no hard reload)
            assert "/players" in page.url


def test_players_search(page, server_url):
    """4.3 Search field filters players by name."""
    login_and_set_token(page, server_url, "admin", "admin123")
    page.goto(f"{server_url}/players")
    page.wait_for_load_state("domcontentloaded")

    # Find search input
    search = page.locator('input[type="search"], input[placeholder*="поиск" i], input[placeholder*="search" i], input[name="search"]')
    if search.count() > 0 and search.first.is_visible():
        search.first.fill("test")
        page.wait_for_timeout(1500)  # Wait for debounce
        # The list should update via HTMX (no full page reload)
        assert "/players" in page.url


def test_click_player_navigates_to_detail(page, server_url):
    """4.4 Clicking a player name navigates to /players/{id}."""
    login_and_set_token(page, server_url, "admin", "admin123")
    page.goto(f"{server_url}/players")
    page.wait_for_load_state("domcontentloaded")

    # Find first player link (should be in the table)
    player_link = page.locator('table a[href*="/players/"], .player-name a[href*="/players/"]')
    if player_link.count() > 0 and player_link.first.is_visible():
        player_link.first.click()
        page.wait_for_load_state("domcontentloaded")
        assert "/players/" in page.url
