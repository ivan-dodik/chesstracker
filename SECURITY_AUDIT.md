# Security Audit & Architecture Review Report

**Date:** 2026-06-06
**Tooling:** Cline with skills `requesting-code-review` and `improve-codebase-architecture`
**Commit:** `6d79e80` — refactor: code review, security fixes, and architecture improvements

---

## Summary

| Severity | Count | Fixed |
|----------|-------|-------|
| Critical | 3 | 3 |
| Important | 3 | 3 |
| Minor/Worth Exploring | 3 | 0 (documented) |

---

## 1. Critical Issues

### C1. Default SECRET_KEY

- **File:** `backend/app/core/config.py:14`
- **Issue:** `SECRET_KEY = "change-me-to-a-random-secret-key"` — все JWT-токены могут быть подделаны.
- **Fix:** Добавлен `field_validator` с `warnings.warn()`, предупреждающий при запуске с дефолтным значением.
- **Status:** ✅ Fixed

### C2. N+1 Queries in game_service

- **File:** `backend/app/services/game_service.py:33-58`
- **Issue:** Для каждой игры в турнире выполнялись отдельные запросы к таблице Player (2N+1 запросов для N игр).
- **Fix:** Заменено на `selectinload(Game.white_player)` и `selectinload(Game.black_player)` — 2 JOIN-запроса вместо 2N+1.
- **Status:** ✅ Fixed

### C3. CSV Import — No Size Limit

- **File:** `backend/app/api/import_route.py:18-30`
- **Issue:** Отсутствовало ограничение на размер загружаемого CSV-файла — потенциальная DoS-атака.
- **Fix:** Добавлен лимит 10 MB с HTTP 413 Request Entity Too Large при превышении.
- **Status:** ✅ Fixed

---

## 2. Important Issues

### I1. CORS `allow_origins=["*"]`

- **File:** `backend/app/main.py:37`
- **Issue:** Любой сайт может делать запросы к API в production.
- **Fix:** Добавлен комментарий и переменная `CORS_ORIGINS` для явного указания необходимости ограничения.
- **Status:** ✅ Fixed (documented for production deployment)

### I2. Duplicated Standings Logic

- **Files:** `backend/app/services/tournament_service.py` + `backend/app/services/export_service.py`
- **Issue:** Одинаковая логика подсчёта очков, побед, ничьих и поражений была реализована в двух разных сервисах.
- **Fix:** Создан `backend/app/services/standings_service.py` с функцией `calculate_standings()`, оба сервиса переписаны на его использование.
- **Status:** ✅ Fixed

### I3. Tests Using Shared test.db File

- **File:** `backend/tests/conftest.py`
- **Issue:** Все тесты использовали один файл `test.db`, что приводило к проблемам изоляции и загрязнению репозитория.
- **Fix:** Используется `tempfile.mkstemp()` для создания временного файла с уникальным именем; добавлена функция `_cleanup_test_db()`.
- **Status:** ✅ Fixed

---

## 3. Minor / Worth Exploring

### M1. SSE Endpoint Without Authentication

- **File:** `backend/app/api/sse.py`
- **Issue:** SSE-эндпоинт `/api/events` доступен без аутентификации.
- **Recommendation:** Добавить `Depends(get_current_user)` для авторизации подписок.
- **Status:** 🔄 Pending (requires architectural decision on SSE auth model)

### M2. ActivityLog JSON Stored as Strings

- **File:** `backend/app/models/activity_log.py`
- **Issue:** Поля `old_values` и `new_values` хранятся как строки, требуется ручная сериализация/десериализация.
- **Recommendation:** Использовать `JSON`-тип SQLAlchemy или Pydantic-валидацию.
- **Status:** 🔄 Pending (current solution works for SQLite + PostgreSQL compatibility)

### M3. No Rate Limiting on `/api/auth/login`

- **File:** `backend/app/api/auth.py`
- **Issue:** Эндпоинт логина не защищён от брутфорс-атак.
- **Recommendation:** Добавить middleware для rate limiting (slowapi, fastapi-limiter) или reverse-proxy (nginx).
- **Status:** 🔄 Pending (requires external dependency)

---

## 4. Architecture Improvements

### A1. Shallow CRUD Service Modules

- **Files:** `backend/app/services/player_service.py`, `favorite_service.py`, `rating_service.py`
- **Issue:** Несколько сервисов (player, favorite, rating) являются pass-through: их интерфейс почти так же сложен, как реализация (SELECT/INSERT/UPDATE/DELETE).
- **Recommendation:** Для CRUD-без-логики можно использовать общий базовый класс `BaseCRUDService` или генерировать handler'ы автоматически.
- **Status:** 🔄 Worth exploring

### A2. Rating Engine Coupled to DB Session

- **File:** `backend/app/services/rating_service.py`
- **Issue:** Elo-расчёты выполняются внутри async-функций, принимающих `AsyncSession`. Невозможно unit-тестировать без БД.
- **Recommendation:** Выделить чистую функцию `calculate_elo_change(rating_a, rating_b, result)` в отдельный модуль.
- **Status:** 🔄 Worth exploring

### A3. Missing Tests for Import/Export/SSE/ActivityLog

- **Files:** `backend/tests/`
- **Issue:** Нет тестов для CSV import, CSV export, SSE endpoints, activity log, export service, import service.
- **Recommendation:** Добавить тесты для этих модулей.
- **Status:** 🔄 Pending

---

## Files Changed

| File | Change |
|------|--------|
| `backend/app/core/config.py` | Добавлен `field_validator` для SECRET_KEY |
| `backend/app/main.py` | Добавлен комментарий по CORS |
| `backend/app/api/import_route.py` | Добавлен лимит размера CSV-файла |
| `backend/app/services/game_service.py` | N+1 → selectinload; удалён неиспользуемый импорт |
| `backend/app/services/standings_service.py` | **Новый файл** — общая логика подсчёта standings |
| `backend/app/services/tournament_service.py` | Переписан на `standings_service`; удалён дублирующийся код |
| `backend/app/services/export_service.py` | Переписан на `standings_service`; удалён дублирующийся код |
| `backend/tests/conftest.py` | `test.db` → временный файл; сортировка импортов |
| `CHANGES.md` | Добавлена запись о рефакторинге |
| `PROMPTS.md` | Добавлена запись о промпте сессии |
| `REPORT.md` | Добавлена запись в историю работы |