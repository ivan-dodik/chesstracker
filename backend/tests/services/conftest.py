"""Test configuration for service-layer unit tests.

Uses SQLite (aiosqlite) for isolated, fast tests without Docker.
The engine and session are set up to test service functions directly.
"""

import asyncio
import os
import tempfile
from datetime import datetime

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Override settings BEFORE any app modules are loaded
import app.core.config

_test_db_fd, _test_db_path = tempfile.mkstemp(suffix=".db", prefix="chess_tracker_svc_test_")
app.core.config.settings.DATABASE_URL = f"sqlite+aiosqlite:///{_test_db_path}"

from app.core.database import Base  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models import (  # noqa: E402
    Player,
    Tournament,
    User,
)

TEST_DATABASE_URL = f"sqlite+aiosqlite:///{_test_db_path}"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def _cleanup_test_db() -> None:
    """Remove the temporary test database file."""
    try:
        os.close(_test_db_fd)
        os.unlink(_test_db_path)
    except OSError:
        pass


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create tables before each test and drop them after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Provide a clean database session for each test."""
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
async def sample_player(db_session: AsyncSession) -> Player:
    """Create a sample player for testing."""
    player = Player(name="Test Player", rating=1500, city="Test City")
    db_session.add(player)
    await db_session.flush()
    await db_session.refresh(player)
    return player


@pytest_asyncio.fixture
async def sample_tournament(db_session: AsyncSession) -> Tournament:
    """Create a sample tournament for testing."""
    tournament = Tournament(
        name="Test Tournament",
        start_date=datetime(2026, 1, 1),
        end_date=datetime(2026, 1, 10),
        location="Test Location",
        rounds=5,
        type="classic",
        status="active",
    )
    db_session.add(tournament)
    await db_session.flush()
    await db_session.refresh(tournament)
    return tournament


@pytest_asyncio.fixture
async def sample_user(db_session: AsyncSession) -> User:
    """Create a sample user for testing."""
    user = User(username="testuser", hashed_password=hash_password("testpass"), role="user")
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_admin(db_session: AsyncSession) -> User:
    """Create a sample admin for testing."""
    admin = User(username="admin", hashed_password=hash_password("admin123"), role="admin")
    db_session.add(admin)
    await db_session.flush()
    await db_session.refresh(admin)
    return admin
