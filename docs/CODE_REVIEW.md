# Код-ревью проекта Chess Tracker

**Дата:** 2026-06-14  
**Объём:** Backend (FastAPI + SQLAlchemy), Frontend (HTMX + Alpine.js + Chart.js), Telegram-bot, Infrastructure (Docker, CI)  
**Метод:** Статический анализ всех исходных файлов проекта

---

## Сводка

| Severity | Кол-во | Описание |
|----------|--------|----------|
| 🔴 Critical | 5 | Security — требуют немедленного исправления |
| 🟠 High | 5 | Architecture / Performance |
| 🟡 Medium | 5 | Code Quality / Maintainability |
| 🟢 Low | 7 | Cleanup / Best Practices |
| **Итого** | **22** | |

---

## 🔴 Critical — Security

### CR-1: CORS `allow_origins=["*"]` с `allow_credentials=True`

**Файл:** `backend/app/main.py:38-45`  
**Проблема:** Комбинация wildcard origin с credentials — браузеры отклоняют такой CORS, но в некоторых конфигурациях (reverse proxy) это может привести к обходу Same-Origin Policy. Атакующий с любого origin может делать authenticated requests.

```python
# Текущий код (main.py:38-45)
CORS_ORIGINS = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,  # ⚠️ Dangerous with wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Рекомендация:** Использовать explicit allowlist из env-переменной:

```python
CORS_ORIGINS = settings.CORS_ORIGINS  # ["http://localhost:8000", "https://chesstracker.example.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

### CR-2: JWT в cookie без `HttpOnly` и `Secure` флагов

**Файл:** `backend/app/static/js/main.js:119`  
**Проблема:** Токен сохраняется через `document.cookie`, что делает его доступным через JavaScript. При XSS-уязвимости атакующий украдёт JWT.

```javascript
// Текущий код (main.js:119)
document.cookie = `jwt_token=${data.access_token}; path=/; max-age=86400; SameSite=Lax`;
```

**Рекомендация:** Устанавливать cookie на сервере (endpoint `/api/auth/login`) с флагами `HttpOnly; Secure; SameSite=Lax`. На клиенте — только `localStorage` (уже есть) или только server-side cookie.

```python
# На стороне сервера (в auth.py login endpoint)
response.set_cookie(
    key="jwt_token",
    value=access_token,
    httponly=True,      # Недоступен через JS
    secure=True,        # Только HTTPS
    samesite="lax",
    max_age=86400,
    path="/",
)
```

---

### CR-3: Seed-пароли захардкожены в коде

**Файл:** `backend/app/seed.py:100-109`  
**Проблема:** `admin123` и `user123` захардкожены. Если seed запущен в production (или эти пароли попадут в документацию/логи), система скомпрометирована.

```python
# Текущий код (seed.py:100-109)
admin = User(username="admin", hashed_password=hash_password("admin123"), role="admin")
user = User(username="user", hashed_password=hash_password("user123"), role="user")
```

**Рекомендация:** Генерировать пароли через env-переменные или random, добавить guard от запуска в production:

```python
import os
if os.getenv("ENVIRONMENT") == "production":
    raise RuntimeError("Seed script must not run in production")
```

---

### CR-4: HS256 JWT алгоритм — симметричный ключ

**Файл:** `backend/app/core/security.py:28,34`  
**Проблема:** HS256 использует один секрет для подписи и валидации. При утечке `SECRET_KEY` атакующий может подписать произвольные токены.

```python
# Текущий код (security.py:28)
return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
```

**Рекомендация:** Для production рассмотреть RS256 (asymmetric). Для student-проекта HS256 допустим, но SECRET_KEY должен быть >= 32 bytes и храниться только в env.

---

### CR-5: `int(user_id)` без guard от ValueError

**Файл:** `backend/app/api/deps.py:44-51`  
**Проблема:** Если `payload.get("sub")` содержит нечисловую строку, `int(user_id)` выбросит `ValueError` → необработанный 500.

```python
# Текущий код (deps.py:44-51)
user_id = payload.get("sub")
if user_id is None:
    raise HTTPException(...)
result = await db.execute(select(User).where(User.id == int(user_id)))
```

**Рекомендация:**

```python
try:
    user_id_int = int(user_id)
except (ValueError, TypeError):
    raise HTTPException(status_code=401, detail="Invalid token payload")
result = await db.execute(select(User).where(User.id == user_id_int))
```

---

## 🟠 High — Architecture / Performance

### CR-6: N+1 агрегация stats_service — загрузка всех игр в память

**Файлы:** `backend/app/services/stats_service.py:9-50, 63-103`  
**Проблема:** `get_head_to_head()` и `get_overall_stats()` загружают **все** Game объекты в Python, затем итеративно подсчитывают. При 1000+ игр — O(n) Python loop + memory overhead.

```python
# Текущий код (stats_service.py:22-23)
result = await db.execute(query)
games = list(result.scalars().all())  # Все игры в память
for game in games:  # Python loop
    if game.result == "1-0": ...
```

**Рекомендация:** Использовать SQL агрегацию:

```python
from sqlalchemy import case, func

query = select(
    func.count(Game.id).label("total_games"),
    func.count(case((Game.result == "1-0", 1))).label("white_wins"),
    func.count(case((Game.result == "0-1", 1))).label("black_wins"),
    func.count(case((Game.result == "½-½", 1))).label("draws"),
).where(
    or_(
        (Game.white_player_id == player1_id) & (Game.black_player_id == player2_id),
        (Game.white_player_id == player2_id) & (Game.black_player_id == player1_id),
    )
).where(Game.result.isnot(None))
```

---

### CR-7: Auto-commit в `get_db()` для всех запросов

**Файл:** `backend/app/api/deps.py:22-32`  
**Проблема:** Каждый GET-запрос (чтение) коммитит сессию. Это избыточно и может вызвать concurrency issues.

```python
# Текущий код (deps.py:24-32)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()  # Каждый request коммитит
        except Exception:
            await session.rollback()
            raise
```

**Рекомендация:** Разделить на read/write сессии или коммитить только при наличии изменений:

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            if session.is_modified:
                await session.commit()
        except Exception:
            await session.rollback()
            raise
```

---

### CR-8: Нет rate limiting на auth endpoints

**Файл:** `backend/app/api/auth.py`  
**Проблема:** `/api/auth/login` не имеет ограничений на количество попыток. Brute-force атака на пароль возможна без ограничений.

**Рекомендация:** Добавить `slowapi` или простой in-memory rate limiter:

```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")
async def login(...):
```

---

### CR-9: CSV import загружает весь файл в память

**Файл:** `backend/app/services/import_service.py:41-42`  
**Проблема:** `csv.DictReader(io.StringIO(csv_content))` — весь CSV загружается в строку, затем в память. Для больших файлов (10к+ строк) — OOM risk.

```python
# Текущий код (import_service.py:41-42)
reader = csv.DictReader(io.StringIO(csv_content))
rows = list(reader)  # Все строки в память
```

**Рекомендация:** Добавить limit на размер CSV в endpoint'е:

```python
if len(csv_content) > 10 * 1024 * 1024:  # 10MB limit
    return {"success": False, "error": "File too large (max 10MB)"}
```

---

### CR-10: `async def` для синхронных функций

**Файл:** `backend/app/services/import_service.py:13`  
**Проблема:** `parse_result()` объявлена `async def` но не содержит `await`. Это создаёт ненужный coroutine object при вызове.

```python
# Текущий код (import_service.py:13)
async def parse_result(result_str: str) -> str | None:
    result_str = result_str.strip()  # sync-only operations
    ...
```

**Рекомендация:** Убрать `async`:

```python
def parse_result(result_str: str) -> str | None:
```

---

## 🟡 Medium — Code Quality

### CR-11: Дублирование logic wins/losses/draws в 4 местах

**Файлы:** `stats_service.py`, `standings_service.py`, `export_service.py`  
**Проблема:** Одинаковый pattern подсчёта результатов повторяется минимум 4 раза. При изменении формата результата — нужно менять везде.

**Рекомендация:** Вынести в shared helper:

```python
# app/services/result_utils.py
def classify_result(result: str, player_id: int, white_player_id: int) -> str:
    """Return 'win', 'loss', or 'draw' for the given player."""
    if result == "½-½":
        return "draw"
    winner_is_white = result == "1-0"
    player_is_white = player_id == white_player_id
    return "win" if winner_is_white == player_is_white else "loss"
```

---

### CR-12: `RatingHistory.tournament_id` — orphan FK

**Файл:** `backend/app/models/rating_history.py`  
**Проблема:** `tournament_id` — FK на Tournament, но в `Tournament` модели нет `rating_history` relationship. Односторонняя связь.

**Рекомендация:** Добавить в `Tournament`:

```python
rating_history: Mapped[list["RatingHistory"]] = relationship(
    "RatingHistory", back_populates="tournament", lazy="selectin"
)
```

---

### CR-13: `round` — зарезервированное слово Python

**Файл:** `backend/app/models/game.py`  
**Проблема:** `round` — встроенная функция Python. Использование как имя столбца создаёт confusion (хотя SQLAlchemy обрабатывает это корректно).

**Рекомендация:** Рассмотреть переименование в `game_round` или `round_number`.

---

### CR-14: Console.log в production JS

**Файл:** `backend/app/static/js/main.js:91-143`  
**Проблема:** 8+ `console.log` в login flow. В production — information leakage (токены, данные пользователей в консоли).

```javascript
// Текущий код (main.js:91,103,114,120,128,132,139)
console.log('[Login] Attempting login for user:', this.username);
console.log('[Login] Login response status:', response.status);
console.log('[Login] Login successful, token received');
// ...
```

**Рекомендация:** Убрать или обернуть в conditional logging:

```javascript
const DEBUG = window.location.hostname === 'localhost';
if (DEBUG) console.log('[Login] ...');
```

---

### CR-15: `generate_rating_change()` может вернуть 0

**Файл:** `backend/app/seed.py:49-52`  
**Проблема:** `max(0, ...)` — при маленьком рейтинге может вернуть 0, что нереалистично.

```python
# Текущий код (seed.py:52)
return max(0, current_rating + delta)
```

**Рекомендация:**

```python
return max(100, current_rating + delta)
```

---

## 🟢 Low — Cleanup / Best Practices

### CR-16: Нет `.dockerignore`

**Файл:** (отсутствует)  
**Проблема:** `.git/`, `tests/`, `e2e/`, `.env` попадают в Docker build context.

**Рекомендация:** Создать `.dockerignore`:

```
.git
tests
e2e
.env
.env.*
*.md
screenshots
node_modules
__pycache__
```

---

### CR-17: Tests копируются в production image

**Файл:** `backend/Dockerfile`  
**Проблема:** `COPY tests/ ./tests/` и `COPY e2e/ ./e2e/` увеличивают образ и расширяют attack surface.

**Рекомендация:** Убрать копирование tests из production stage или использовать multi-stage build.

---

### CR-18: Telegram-bot depends on `service_started` вместо `service_healthy`

**Файл:** `docker-compose.yml`  
**Проблема:** Bot стартует до готовности backend → ошибки подключения при первом запуске.

**Рекомендация:**

```yaml
telegram-bot:
  depends_on:
    backend:
      condition: service_healthy
```

---

### CR-19: `passlib` не поддерживается + `bcrypt==4.0.1` pin

**Файл:** `backend/pyproject.toml`  
**Проблема:** `passlib[bcrypt]>=1.7.4` — проект заброшен с 2020. `bcrypt==4.0.1` — хрупкий pin.

**Рекомендация:** Перейти на прямое использование `bcrypt`:

```python
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())
```

---

### CR-20: SSE reconnect без reset delay

**Файл:** `backend/app/static/js/sse.js:67`  
**Проблема:** Delay растёт экспоненциально но не сбрасывается после успешного reconnect.

```javascript
// Текущий код (sse.js:67)
this.currentDelay = Math.min(this.currentDelay * 1.5, this.maxReconnectDelay);
```

**Рекомендация:** Добавить reset в `onopen`:

```javascript
this.eventSource.onopen = () => {
    this.currentDelay = this.reconnectDelay;  // Reset
};
```

---

### CR-21: Duplicate `loadPlayers()` в Alpine.js компонентах

**Файл:** `backend/app/static/js/main.js:198-205, 276-284`  
**Проблема:** `ratingChart` и `overallStatsChart` содержат идентичный метод `loadPlayers()`.

**Рекомендация:** Вынести в shared Alpine store:

```javascript
Alpine.store('players', {
    items: [],
    loaded: false,
    async load() {
        if (this.loaded) return;
        const resp = await fetch('/api/players?per_page=100', { headers: Auth.getAuthHeaders() });
        const data = await resp.json();
        this.items = data.items || [];
        this.loaded = true;
    }
});
```

---

### CR-22: Нет healthcheck в Docker Compose

**Файл:** `docker-compose.yml`  
**Проблема:** Backend не имеет healthcheck → `depends_on` не может ждать готовности сервиса.

**Рекомендация:**

```yaml
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 10s
    timeout: 5s
    retries: 3
```

---

## Позитивные замечания

Проект демонстрирует высокий уровень工程质量:

- ✅ **Чистая архитектура**: Чёткое разделение API / Services / Models / Schemas
- ✅ **E2E тесты**: 29 Playwright тестов покрывают основные user flows
- ✅ **Activity log**: Аудит всех операций CRUD — хорошая практика
- ✅ **SSE для real-time**: Правильный выбор вместо WebSocket для данной задачи
- ✅ **Pre-commit hooks**: ruff + pytest блокируют bad commits
- ✅ **Альтернативный фронтенд**: HTMX + Alpine.js — минимальный JS footprint
- ✅ **Alembic миграции**: История миграций с самого начала
- ✅ **Seed data**: Достаточные тестовые данные для разработки и демо
- ✅ **CSV import/export**: Поддержка двух форматов с авто-определением

---

## Приоритеты исправления

| Приоритет | Issues | Время (оценка) |
|-----------|--------|----------------|
| P0 — Немедленно | CR-1, CR-2, CR-5 | 2-3 часа |
| P1 — До релиза | CR-3, CR-4, CR-8 | 3-4 часа |
| P2 — Ближайший спринт | CR-6, CR-7, CR-9, CR-10 | 4-6 часов |
| P3 — Техдолг | CR-11 — CR-22 | 6-8 часов |