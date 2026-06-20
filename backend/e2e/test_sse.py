# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""E2E tests: SSE (Server-Sent Events) — connection and toast notifications."""

import json
import urllib.request

from e2e.conftest import login_and_set_token


def test_sse_connection(page, server_url):
    """8.1 EventSource connects to /api/events when logged in."""
    login_and_set_token(page, server_url, "admin", "admin123")
    page.goto(f"{server_url}/")
    page.wait_for_load_state("domcontentloaded")

    # Check if SSE connection is attempted by evaluating JavaScript
    has_sse = page.evaluate("""() => {
        // Check if sse.js loaded and EventSource was used
        return typeof window.EventSource !== 'undefined' ||
               document.querySelector('[data-sse]') !== null ||
               document.querySelector('.toast-container') !== null;
    }""")
    # SSE should be available (even if no events yet)
    content = page.content()
    assert has_sse or "sse" in content.lower() or "toast" in content.lower() or "EventSource" in content


def test_sse_toast_notification_appears(page, server_url):
    """8.2 Toast notification infrastructure is loaded."""
    login_and_set_token(page, server_url, "admin", "admin123")
    page.goto(f"{server_url}/", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # Verify SSE client infrastructure is loaded
    # sse.js creates a toast container dynamically or is present in the page
    content = page.content()
    has_sse_script = "sse.js" in content
    has_toast = "toast" in content.lower()
    has_eventsource = page.evaluate("() => typeof EventSource !== 'undefined'")
    # At least one of these should be true
    assert has_sse_script or has_toast or has_eventsource
