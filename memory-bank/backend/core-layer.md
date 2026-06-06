# Core Layer (`app/core/`)

## Files

- `config.py` — `Settings(BaseSettings)`: DATABASE_URL, SECRET_KEY, TG_BOT_TOKEN, BACKEND_URL, DEBUG
- `database.py` — async engine, session factory, `Base(DeclarativeBase)`, `get_db()` dependency
- `security.py` — `hash_password()`, `verify_password()` (bcrypt), `create_access_token()`, `decode_access_token()` (JWT HS256)

## Key exports

| Export             | Type                | Purpose                            |
|--------------------|---------------------|------------------------------------|
| `settings`         | `Settings` instance | Singleton with all env config      |
| `engine`           | `AsyncEngine`       | SQLAlchemy async engine            |
| `async_session_factory` | `async_sessionmaker` | Session factory (expire_on_commit=False) |
| `Base`             | `DeclarativeBase`   | ORM base class for all models      |
| `get_db()`         | async generator     | FastAPI dependency → `AsyncSession` |

## Settings (config.py)

| Variable                   | Default                               | Notes                  |
|----------------------------|---------------------------------------|------------------------|
| `DATABASE_URL`             | `postgresql+asyncpg://...`            | Overridden in tests    |
| `SECRET_KEY`               | `change-me-to-a-random-secret-key`    | JWT signing key        |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 1440 (24h)                         | JWT lifetime           |
| `TG_BOT_TOKEN`             | `""`                                  | Telegram bot token     |
| `BACKEND_URL`              | `http://backend:8000`                 | Used by telegram-bot   |
| `DEBUG`                    | `True`                                | Enables SQLAlchemy echo|

## Security (security.py)

- `pwd_context = CryptContext(schemes=["bcrypt"])`
- `hash_password("plain") → str`
- `verify_password("plain", "hash") → bool`
- `create_access_token({"sub": user_id, "role": role}) → JWT str`
- `decode_access_token(token) → dict | None`

## Database (database.py)

- `engine = create_async_engine(DATABASE_URL, echo=settings.DEBUG)`
- `async_session_factory = async_sessionmaker(engine, expire_on_commit=False)`
- `get_db()` — yields session, commits on success, rolls back on exception, closes in finally

## Dependencies (`api/deps.py` — linked, not in core/)

- `get_db()` — from database.py
- `get_current_user()` — extracts JWT from `Authorization: Bearer`, returns `User`
- `get_current_admin()` — wraps `get_current_user`, checks `role == "admin"`, raises 403

## Test overrides

In tests (`conftest.py`):
- `settings.DATABASE_URL` overridden to `sqlite+aiosqlite:///./test.db` **before** any imports
- Separate `engine` and `TestSessionLocal` using SQLite
- `app.dependency_overrides[get_db] = override_get_db` routes sessions to test DB

## Links

- → `modules/models-layer.md` (models import Base from core/database.py)
- → `modules/api-layer.md` (deps.py used by all routers)
- → `modules/testing.md` (test DB override mechanism)