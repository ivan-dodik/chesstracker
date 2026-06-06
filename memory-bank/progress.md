# Progress: Chess Tracker

## Текущий статус
**M5: Backend — API: специфичные фичи** завершён. Все специфичные API эндпоинты созданы, протестированы (20/20 passed) и запушены.

## Что работает
- ✅ **M1: Архитектура и планирование** — полная документация
- ✅ **M2: Окружение и Docker** — Docker Compose, Dockerfile, pyproject.toml
- ✅ **M3: Backend — модели и БД**
  - ✅ Core: config.py (pydantic-settings), database.py (async engine), security.py (JWT, bcrypt)
  - ✅ Модели: User, Player, Tournament, Game, RatingHistory, Favorite, ActivityLog
  - ✅ Alembic: async env.py, миграция "initial" накатана (8 таблиц)
  - ✅ Pydantic схемы: User, Player, Tournament, Game, RatingHistory, Favorite, ActivityLog
  - ✅ Seed: 2 user, 30 players, 10 tournaments, 258 games, 180 rating_history, 4 favorites, 3 activity_logs
  - ✅ bcrypt зафиксирован на 4.0.1 (совместимость с passlib)
- ✅ **M4: Backend — API: аутентификация и базовые CRUD**
  - ✅ deps.py: get_db, get_current_user, get_current_admin
  - ✅ auth.py: POST /api/auth/login, /register, /me
  - ✅ players.py: CRUD + поиск/фильтрация/пагинация
  - ✅ tournaments.py: CRUD + поиск/фильтрация + standings
  - ✅ games.py: CRUD по турам + подсчёт очков
  - ✅ router.py + main.py
  - ✅ Тесты: 8/8 passed (test_auth.py: 4, test_players.py: 4)
  - ✅ Docker build успешен, все эндпоинты проверены через curl
- ✅ **M5: Backend — API: специфичные фичи**
  - ✅ rating_service + API: история рейтинга с фильтром по дате
  - ✅ favorite_service + API: CRUD избранного
  - ✅ stats_service + API: head-to-head, top-rated, overall stats
  - ✅ sse_service + API: Server-Sent Events с keepalive
  - ✅ export_service + API: CSV экспорт турнирной таблицы
  - ✅ import_service + API: CSV импорт (2 формата)
  - ✅ activity_log_service + API: лог активности с фильтрацией
  - ✅ Интеграция ActivityLog во все CRUD (players, tournaments, games)
  - ✅ Интеграция SSE-событий при создании/обновлении партий
  - ✅ Тесты: 20/20 passed (test_ratings: 3, test_stats: 4, test_favorites: 5)
  - ✅ Docker build успешен

## Что осталось сделать (в порядке приоритета)

### M6: Frontend — базовая структура и навигация
- ⬜ Шаблоны, CSS, JS, HTMX-фрагменты, web-роуты
- ⬜ Проверить, что все страницы открываются

### M7: Frontend — дашборд и детальные страницы
- ⬜ Chart.js, Alpine.js, профили, детали турниров

### M8: Frontend — фичи
- ⬜ Избранное, SSE, CSV, аутентификация

### M9: Telegram-bot
- ⬜ bot.py, handlers, api_client, notifier

### M10: Тестирование и CI
- ⬜ GitHub Actions, pre-commit hook

### M11: Финальная документация
- ⬜ README.md, финальная проверка

## Известные проблемы
- **bcrypt 5.x** несовместим с passlib 1.7.4 — зафиксирована версия 4.0.1
- **ruff** выдаёт ошибки в app/ (преимущественно в seed.py и моделях) — будут исправлены в M10 при настройке CI

## Эволюция проектных решений
- **2026-06-06**: Инициализация
- **2026-06-06 13:35**: IMPLEMENTATION_PLAN, архитектурные решения
- **2026-06-06 14:17**: M2 завершён — Docker-инфраструктура
- **2026-06-06 14:38**: M3 завершён — модели, миграции, схемы, seed
- **2026-06-06 16:40**: M4 завершён — API: auth + CRUD + тесты 8/8