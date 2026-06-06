# Test Fixtures

## API test fixtures (`tests/conftest.py`)

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `event_loop` | session | Session-scoped event loop for async tests |
| `setup_database` | function (autouse) | Creates all tables before test, drops after |
| `client` | function | `httpx.AsyncClient` with `ASGITransport(app=app)` |
| `admin_token` | function | Creates admin user → returns `{"Authorization": "Bearer <JWT>"}` |
| `user_token` | function | Creates regular user → returns `{"Authorization": "Bearer <JWT>"}` |

### DB override mechanism
```python
# Before any app imports
settings.DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Separate engine + session for tests
engine = create_async_engine(settings.DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Override FastAPI dependency
app.dependency_overrides[get_db] = override_get_db
```

### Helper function
```python
async def _create_user_in_test_db(username: str, password: str, role: str) -> User:
    """Creates a user directly in the test DB and returns the User object."""
```

## Service test fixtures (`tests/services/conftest.py`)

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `event_loop` | session | Session-scoped event loop |
| `setup_database` | function (autouse) | create_all/drop_all per test |
| `db_session` | function | Clean `AsyncSession` with commit/rollback |
| `sample_player` | function | `Player(name="Test Player", rating=1500, city="Test City")` |
| `sample_tournament` | function | `Tournament(name="Test Tournament", rounds=5, type="classic", status="active")` |
| `sample_user` | function | `User(username="testuser", role="user")` |
| `sample_admin` | function | `User(username="admin", role="admin")` |

### Service test DB setup
```python
# Same SQLite override as API tests
settings.DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(settings.DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
```

## Links
- → `testing/overview.md` — test structure
- → `backend/core-layer.md` — DB override mechanism