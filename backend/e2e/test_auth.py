"""E2E tests: Authentication — login, logout, page protection."""

from e2e.conftest import login, login_and_set_token


def test_login_success_admin(page, server_url):
    """1.1 Successful admin login → redirect to dashboard, show username."""
    login(page, server_url, "admin", "admin123")
    assert "/login" not in page.url
    assert page.url.rstrip("/") == server_url  # on dashboard
    # Navbar should show the username
    nav_user = page.locator(".username")
    assert nav_user.text_content().strip() == "admin"


def test_login_success_user(page, server_url):
    """1.2 Successful user login → redirect to dashboard."""
    login(page, server_url, "user", "user123")
    assert "/login" not in page.url
    nav_user = page.locator(".username")
    assert nav_user.text_content().strip() == "user"


def test_login_failure(page, server_url):
    """1.3 Wrong password → error message, stay on /login."""
    page.goto(f"{server_url}/login", wait_until="domcontentloaded")
    page.wait_for_selector("#username", state="visible")
    page.fill("#username", "admin")
    page.fill("#password", "wrongpassword")
    page.click('button[type="submit"]')
    # Should stay on /login and show error
    page.wait_for_timeout(2000)
    assert "/login" in page.url
    # Alpine.js error message should be visible
    error_el = page.locator("[x-text='error']")
    assert error_el.is_visible()
    assert len(error_el.text_content().strip()) > 0


def test_protected_page_redirects_to_login(page, server_url):
    """1.4 Accessing /players without JWT → redirect to /login."""
    page.goto(f"{server_url}/players", wait_until="domcontentloaded")
    page.wait_for_timeout(1000)
    # Should redirect to /login (cookie-based auth for web routes)
    assert "/login" in page.url


def test_logout(page, server_url):
    """1.5 Logout → clear JWT, show 'Войти' button."""
    login_and_set_token(page, server_url, "admin", "admin123")
    # Verify we are logged in
    page.goto(f"{server_url}/", wait_until="domcontentloaded")
    page.wait_for_timeout(500)
    assert page.locator(".username").is_visible()
    # Click logout
    page.click("text=Выйти")
    page.wait_for_timeout(1000)
    # Should show "Войти" link
    login_link = page.locator('a[href="/login"]')
    assert login_link.is_visible()
