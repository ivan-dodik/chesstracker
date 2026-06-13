"""Test configuration and fixtures.

IMPORTANT: The engine and session are created using SQLite (aiosqlite)
for isolated, fast tests. The DATABASE_URL in settings is overridden
at module load time to prevent asyncpg from being used during tests.
"""

import asyncio
import os
import tempfile
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Override settings BEFORE any app modules are loaded
import app.core.config

# Use a temporary file for SQLite to avoid in-memory isolation issues
_test_db_fd, _test_db_path = tempfile.mkstemp(suffix=".db", prefix="chess_tracker_test_")
app.core.config.settings.DATABASE_URL = f"sqlite+aiosqlite:///{_test_db_path}"

from app.core.database import Base, get_db  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.main import app  # noqa: E402
from app.models import User  # noqa: E402

TEST_DATABASE_URL = f"sqlite+aiosqlite:///{_test_db_path}"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


def _cleanup_test_db() -> None:
    """Remove the temporary test database file."""
    try:
        os.close(_test_db_fd)
        os.unlink(_test_db_path)
    except OSError:
        pass


@pytest.fixture(autouse=True)
def _disable_rate_limiter():
    """Disable rate limiter during tests (official slowapi approach)."""
    from app.api.auth import limiter
    limiter.enabled = False
    yield
    limiter.enabled = True


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create tables before each test and drop them after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override the get_db dependency to use test database."""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with overridden database dependency."""
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


async def _create_user_in_test_db(username: str, password: str, role: str = "user") -> User:
    """Helper to create a user in the test database."""
    async with TestSessionLocal() as session:
        user = User(username=username, hashed_password=hash_password(password), role=role)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient) -> str:
    """Create an admin user and return JWT token."""
    await _create_user_in_test_db("admin", "admin123", role="admin")
    response = await client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def user_token(client: AsyncClient) -> str:
    """Create a regular user and return JWT token."""
    await _create_user_in_test_db("user", "user123", role="user")
    response = await client.post("/api/auth/login", json={"username": "user", "password": "user123"})
    return response.json()["access_token"]
