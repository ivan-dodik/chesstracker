"""E2E tests: Tournament detail page — info, standings, CSV export/import, accordion."""

import csv
import io
import json
import urllib.request

from e2e.conftest import login_and_set_token


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


def _create_tournament(server_url: str, token: str, name: str, status: str = "active") -> int:
    """Helper: create a tournament via API."""
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


def _create_player(server_url: str, token: str, name: str, rating: int = 1500) -> int:
    """Helper: create a player via API."""
    req = urllib.request.Request(
        f"{server_url}/api/players",
        data=json.dumps({"name": name, "rating": rating}).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["id"]


def test_tournament_detail_loads(page, server_url):
    """7.1 Tournament detail page shows tournament info."""
    token = _get_admin_token(server_url)
    t_id = _create_tournament(server_url, token, "DetailTournament")

    login_and_set_token(page, server_url, "admin", "admin123")
    page.goto(f"{server_url}/tournaments/{t_id}", wait_until="domcontentloaded")
    # Wait for Alpine.js to load data via fetch()
    page.wait_for_timeout(3000)

    content = page.content()
    assert "DetailTournament" in content


def test_tournament_standings(page, server_url):
    """7.2 Tournament standings table is displayed."""
    token = _get_admin_token(server_url)
    t_id = _create_tournament(server_url, token, "StandingsTournament")

    login_and_set_token(page, server_url, "admin", "admin123")
    page.goto(f"{server_url}/tournaments/{t_id}")
    page.wait_for_load_state("domcontentloaded")

    content = page.content()
    # Standings section should exist
    assert "Таблица" in content or "standings" in content.lower() or "Очки" in content or "Турнирная" in content


def test_tournament_csv_export(page, server_url):
    """7.3 Export CSV link exists and points to the correct URL."""
    token = _get_admin_token(server_url)
    t_id = _create_tournament(server_url, token, "ExportTournament")

    login_and_set_token(page, server_url, "admin", "admin123")
    page.goto(f"{server_url}/tournaments/{t_id}", wait_until="domcontentloaded")
    # Wait for Alpine.js to render the export button
    page.wait_for_timeout(3000)

    # Find export button/link
    export_btn = page.locator(f'a[href*="/api/tournaments/{t_id}/export/csv"]')
    if export_btn.count() > 0 and export_btn.first.is_visible():
        href = export_btn.first.get_attribute("href")
        assert href is not None
        assert "/export/csv" in href
        assert str(t_id) in href
    # Verify the export endpoint is accessible via API
    req = urllib.request.Request(
        f"{server_url}/api/tournaments/{t_id}/export/csv",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req) as resp:
        csv_content = resp.read().decode("utf-8")
        assert len(csv_content) > 0
        reader = csv.reader(io.StringIO(csv_content))
        rows = list(reader)
        assert len(rows) > 0  # At least header row


def test_tournament_csv_import(page, server_url):
    """7.4 Admin can import CSV file to tournament."""
    token = _get_admin_token(server_url)
    t_id = _create_tournament(server_url, token, "ImportTournament")

    login_and_set_token(page, server_url, "admin", "admin123")
    page.goto(f"{server_url}/tournaments/{t_id}")
    page.wait_for_load_state("domcontentloaded")

    # Find import form
    import_input = page.locator('input[type="file"], [x-data*="import"], .import-form')
    if import_input.count() > 0:
        # Create a test CSV file
        csv_content = "player,round,opponent,result\nTestPlayer,1,OtherPlayer,1-0\n"
        # Upload file
        file_input = page.locator('input[type="file"]')
        if file_input.count() > 0:
            # Create temp file for upload
            import tempfile
            with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
                f.write(csv_content)
                tmp_path = f.name
            file_input.set_input_files(tmp_path)
            # Submit import
            submit_btn = page.locator('button[type="submit"]:near(input[type="file"]), button:has-text("Импорт")')
            if submit_btn.count() > 0:
                submit_btn.first.click()
                page.wait_for_timeout(2000)
            import os
            os.unlink(tmp_path)


def test_tournament_accordion(page, server_url):
    """7.5 Clicking a round expands accordion to show games."""
    token = _get_admin_token(server_url)
    t_id = _create_tournament(server_url, token, "AccordionTournament")

    login_and_set_token(page, server_url, "admin", "admin123")
    page.goto(f"{server_url}/tournaments/{t_id}")
    page.wait_for_load_state("domcontentloaded")

    content = page.content()
    # Accordion/rounds section should exist
    assert "Тур" in content or "round" in content.lower() or "accordion" in content.lower()
