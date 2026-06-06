# Progress: Chess Tracker

## Текущий статус
**M3: Backend — модели и база данных** завершён. Все модели, миграции, схемы и seed-данные созданы.

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

## Что осталось сделать (в порядке приоритета)

### M4: Backend — API: аутентификация и базовые CRUD
- ⬜ deps.py: get_db, get_current_user, get_current_admin
- ⬜ auth.py: POST /api/auth/login, /register, /me
- ⬜ players.py: CRUD + поиск/фильтрация/пагинация
- ⬜ tournaments.py: CRUD + поиск/фильтрация + standings
- ⬜ games.py: CRUD по турам + подсчёт очков
- ⬜ router.py + main.py (обновление)
- ⬜ Тесты (3–4)

### M5: Backend — API: специфичные фичи
- ⬜ Ratings, Favorites, Stats, Export/Import CSV, SSE, ActivityLog
- ⬜ Тесты (3–4)

### M6: Frontend — базовая структура и навигация
- ⬜ Шаблоны, CSS, JS, HTMX-фрагменты, web-роуты

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
- **ruff** выдаёт 37 ошибок в app/ (преимущественно в seed.py и моделях) — будут исправлены в M10 при настройке CI

## Эволюция проектных решений
- **2026-06-06**: Инициализация
- **2026-06-06 13:35**: IMPLEMENTATION_PLAN, архитектурные решения
- **2026-06-06 14:17**: M2 завершён — Docker-инфраструктура
- **2026-06-06 14:38**: M3 завершён — модели, миграции, схемы, seed