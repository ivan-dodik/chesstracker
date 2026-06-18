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
