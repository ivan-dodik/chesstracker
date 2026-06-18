# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""E2E test configuration — Playwright browser tests against a real FastAPI server.

The server runs on a random port with a temporary SQLite database.
Seed data (admin/user) is created before the server starts.
"""

import os
import tempfile
import time
from collections.abc import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

# ── Shared server state (set by session-scoped fixture) ──────────────

_server_url: str | None = None
_server_proc = None
_test_db_fd: int = -1
_test_db_path: str = ""


def _seed_database(db_path: str) -> None:
    """Seed admin and user accounts into the SQLite test database."""
    import asyncio

    import app.core.config

    app.core.config.settings.DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"

    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from app.core.database import Base  # noqa: E402
    from app.core.security import hash_password  # noqa: E402
    from app.main import app  # noqa: E402
    from app.models import User  # noqa: E402

    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def _seed() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with session_factory() as session:
            admin = User(
                username="admin",
                hashed_password=hash_password("admin123"),
                role="admin",
            )
            user = User(
                username="user",
                hashed_password=hash_password("user123"),
                role="user",
            )
            session.add_all([admin, user])
            await session.commit()
        await engine.dispose()

    asyncio.run(_seed())


@pytest.fixture(scope="session")
def server_url() -> Generator[str]:
    """Start FastAPI server for E2E tests. Yields base URL."""
    import subprocess
    import sys

    global _server_url, _server_proc, _test_db_fd, _test_db_path

    _test_db_fd, _test_db_path = tempfile.mkstemp(suffix=".db", prefix="e2e_test_")

    # Seed database before starting server
    _seed_database(_test_db_path)

    # Find a free port
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    _server_url = f"http://127.0.0.1:{port}"

    # Set DATABASE_URL for the server process
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite+aiosqlite:///{_test_db_path}"
    env["SECRET_KEY"] = "e2e-test-secret-key-must-be-32-chars"

    # Start server
    _server_proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "warning",
        ],
        cwd=os.path.join(os.path.dirname(__file__), ".."),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to be ready
    import urllib.error
    import urllib.request

    for i in range(30):
        time.sleep(0.5)
        try:
            urllib.request.urlopen(f"{_server_url}/login", timeout=2)
            break
        except (urllib.error.URLError, ConnectionError):
            # Check if server process is still alive
            if _server_proc.poll() is not None:
                stderr_out = _server_proc.stderr.read().decode() if _server_proc.stderr else ""
                stdout_out = _server_proc.stdout.read().decode() if _server_proc.stdout else ""
                raise RuntimeError(
                    f"Server process exited with code {_server_proc.returncode}. "
                    f"stdout: {stdout_out[:500]}\nstderr: {stderr_out[:500]}"
                )
            continue
    else:
        stderr_out = _server_proc.stderr.read().decode() if _server_proc.stderr else ""
        _server_proc.terminate()
        raise RuntimeError(
            f"Server did not start within 15 seconds on {_server_url}\n"
            f"stderr: {stderr_out[:500]}"
        )

    yield _server_url

    # Cleanup
    if _server_proc:
        _server_proc.terminate()
        _server_proc.wait(timeout=5)
    try:
        os.close(_test_db_fd)
        os.unlink(_test_db_path)
    except OSError:
        pass


@pytest.fixture(scope="session")
def browserwright() -> Generator[Browser]:
    """Launch Chromium browser for the entire test session."""
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True)
    yield browser
    browser.close()
    pw.stop()


@pytest.fixture()
def context(browserwright: Browser) -> Generator[BrowserContext]:
    """Fresh browser context per test (isolated cookies/storage)."""
    ctx = browserwright.new_context()
    yield ctx
    ctx.close()


@pytest.fixture()
def page(context: BrowserContext, server_url: str) -> Generator[Page]:
    """Fresh page per test."""
    p = context.new_page()
    yield p
    p.close()


def login(page: Page, url: str, username: str, password: str) -> None:
    """Login via the UI form. Navigates to /login, fills form, submits."""
    page.goto(f"{url}/login", wait_until="domcontentloaded")
    page.wait_for_selector("#username", state="visible", timeout=10000)
    page.fill("#username", username)
    page.fill("#password", password)
    page.click('button[type="submit"]')
    # Wait for redirect away from /login (dashboard or wherever)
    page.wait_for_url(lambda u: "/login" not in u, timeout=10000)
    page.wait_for_load_state("domcontentloaded")


def login_and_set_token(page: Page, url: str, username: str, password: str) -> None:
    """Login via API and set JWT in localStorage (faster, no UI interaction)."""
    import json
    import urllib.request

    req = urllib.request.Request(
        f"{url}/api/auth/login",
        data=json.dumps({"username": username, "password": password}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        token = json.loads(resp.read())["access_token"]

    # Navigate to the app first (to set cookies/context)
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(500)  # Wait for JS to initialize
    # Set JWT in localStorage AND cookie (web routes need cookie)
    page.evaluate(f"""() => {{
        localStorage.setItem('jwt_token', '{token}');
        localStorage.setItem('user', JSON.stringify({{username: '{username}', role: '{'admin' if username == 'admin' else 'user'}'}}));
        document.cookie = 'jwt_token={token}; path=/; max-age=86400; SameSite=Lax';
    }}""")


def set_token_only(page: Page, url: str, username: str, password: str) -> None:
    """Set JWT in localStorage and cookie. Navigates to /login (lightweight) first."""
    import json
    import urllib.request as _req

    req = _req.Request(
        f"{url}/api/auth/login",
        data=json.dumps({"username": username, "password": password}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with _req.urlopen(req) as resp:
        token = json.loads(resp.read())["access_token"]

    # Navigate to /login (lightweight, no SSE/API calls) to set tokens on correct origin
    page.goto(f"{url}/login", wait_until="domcontentloaded")
    page.evaluate(f"""() => {{
        localStorage.setItem('jwt_token', '{token}');
        localStorage.setItem('user', JSON.stringify({{username: '{username}', role: '{'admin' if username == 'admin' else 'user'}'}}));
        document.cookie = 'jwt_token={token}; path=/; max-age=86400; SameSite=Lax';
    }}""")
