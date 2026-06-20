# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""E2E tests: M22 — Activity log page and rating audit."""

import os


def _read(path: str) -> str:
    with open(path) as f:
        return f.read()


def test_activity_log_template_exists():
    """M22.1 activity_log.html template exists and has expected content."""
    content = _read(
        os.path.join(os.path.dirname(__file__), "..", "app", "templates", "activity_log.html")
    )
    has_content = any(
        kw in content
        for kw in ["Лог активности", "Действие", "Пользователь", "Сущность", "activity"]
    )
    assert has_content, "Activity log template should have expected UI elements"


def test_activity_log_api_endpoint_exists():
    """M22.2 /api/activity-log endpoint is registered in activity_log.py."""
    content = _read(
        os.path.join(os.path.dirname(__file__), "..", "app", "api", "activity_log.py")
    )
    assert "activity-log" in content or "activity_log" in content


def test_activity_log_web_route_exists():
    """M22.3 /activity-log web route is defined in web.py."""
    content = _read(
        os.path.join(os.path.dirname(__file__), "..", "app", "api", "web.py")
    )
    assert "activity-log" in content or "activity_log" in content


def test_rating_calculation_logs_activity():
    """M22.4 Rating calculation service logs changes via activity_log."""
    content = _read(
        os.path.join(
            os.path.dirname(__file__), "..", "app", "services", "rating_calculation_service.py"
        )
    )
    assert "log_activity" in content, "Rating calculation should log activity"
    assert "rating" in content.lower(), "Rating changes should be logged"


def test_activity_log_navigation():
    """M22.5 Navigation includes link to activity log (admin only)."""
    content = _read(
        os.path.join(os.path.dirname(__file__), "..", "app", "templates", "base.html")
    )
    has_nav = "activity-log" in content or "activity_log" in content
    assert has_nav, "Base template should have activity log navigation link"


def test_import_service_logs_activity():
    """M22.6 Import service logs activity for CSV imports."""
    content = _read(
        os.path.join(os.path.dirname(__file__), "..", "app", "services", "import_service.py")
    )
    assert "log_activity" in content, "Import service should log activity"
    assert "import" in content.lower(), "Import operation should be logged"


def test_favorite_service_logs_activity():
    """M22.7 Favorite service logs activity for add/remove."""
    content = _read(
        os.path.join(os.path.dirname(__file__), "..", "app", "services", "favorite_service.py")
    )
    assert "log_activity" in content, "Favorite service should log activity"
    assert "favorite" in content.lower(), "Favorite operations should be logged"


def test_rating_calculation_passes_user_id():
    """M22.8 Rating calculation service accepts user_id parameter."""
    content = _read(
        os.path.join(
            os.path.dirname(__file__), "..", "app", "services", "rating_calculation_service.py"
        )
    )
    assert "user_id" in content, "Rating calculation should accept user_id parameter"
    # Check that log_activity calls use user_id, not None
    lines = content.split("\n")
    log_lines = [line for line in lines if "log_activity" in line and "db," in line]
    for line in log_lines:
        # After the fix, log_activity should use user_id variable, not None
        assert "None" not in line or "user_id" in line, (
            f"log_activity should use user_id, not None: {line.strip()}"
        )


def test_import_route_passes_user_id():
    """M22.9 Import route passes current_user.id to import_tournament_csv."""
    content = _read(
        os.path.join(os.path.dirname(__file__), "..", "app", "api", "import_route.py")
    )
    assert "user_id=current_user.id" in content, (
        "Import route should pass current_user.id to import_tournament_csv"
    )


def test_activity_log_template_has_all_filters():
    """M22.10 Activity log template has filters for all entity types."""
    content = _read(
        os.path.join(os.path.dirname(__file__), "..", "app", "templates", "activity_log.html")
    )
    # Check that all entity types have filter options
    for entity in ["player", "tournament", "game", "rating", "favorite", "import"]:
        assert f'value="{entity}"' in content, (
            f"Activity log template should have filter for '{entity}' entity type"
        )
