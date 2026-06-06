# Progress: Chess Tracker

## Текущий статус
**M6: Frontend — базовая структура и навигация** завершён. Все HTML-шаблоны, CSS, JavaScript и веб-роуты созданы. 4 страницы (дашборд, логин, игроки, турниры) возвращают HTTP 200. Все 20 тестов проходят.

Memory Bank обновлён: созданы файлы описания модулей в `memory-bank/modules/`.

## Что работает
- ✅ **M1: Архитектура и планирование** — полная документация
- ✅ **M2: Окружение и Docker** — Docker Compose, Dockerfile, pyproject.toml
- ✅ **M3: Backend — модели и БД**
  - ✅ Core: config.py (pydantic-settings), database.py (async engine), security.py (JWT, bcrypt)
  - ✅ Модели: User, Player, Tournament, Game, RatingHistory, Favorite, ActivityLog
  - ✅ Alembic: async env.py, миграция "initial" накатана (8 таблиц)
  - ✅ Pydantic схемы: User, Player, Tournament, Game, RatingHistory, Favorite, ActivityLog
  - ✅ Seed: 2 user, 30 players, 10 tournaments, 225 games, 180 rating_history, 4 favorites
  - ✅ bcrypt зафиксирован на 4.0.1 (совместимость с passlib)
- ✅ **M4: Backend — API: аутентификация и базовые CRUD**
  - ✅ deps.py: get_db, get_current_user, get_current_admin
  - ✅ auth.py: POST /api/auth/login, /register, /me
  - ✅ players.py: CRUD + поиск/фильтрация/пагинация
  - ✅ tournaments.py: CRUD + поиск/фильтрация + standings
  - ✅ games.py: CRUD по турам + подсчёт очков
  - ✅ router.py + main.py
  - ✅ Тесты: 8/8 passed
  - ✅ Docker build успешен
- ✅ **M5: Backend — API: специфичные фичи**
  - ✅ rating_service + API: история рейтинга с фильтром по дате
  - ✅ favorite_service + API: CRUD избранного
  - ✅ stats_service + API: head-to-head, top-rated, overall stats
  - ✅ sse_service + API: Server-Sent Events с keepalive
  - ✅ export_service + API: CSV экспорт турнирной таблицы
  - ✅ import_service + API: CSV импорт (2 формата)
  - ✅ activity_log_service + API: лог активности с фильтрацией
  - ✅ Интеграция ActivityLog во все CRUD
  - ✅ Интеграция SSE-событий при создании/обновлении партий
  - ✅ Тесты: 20/20 passed
  - ✅ Docker build успешен
- ✅ **M6: Frontend — базовая структура и навигация**
  - ✅ CSS: стили для навигации, таблиц, карточек, кнопок, форм, пагинации, дашборда, адаптив
  - ✅ JavaScript: Auth helpers, HTMX config, Alpine.js компоненты, flash-сообщения
  - ✅ Шаблоны: base.html, login.html, index.html, players/list.html, tournaments/list.html
  - ✅ Partials: player_row, tournament_row, pagination
  - ✅ web.py: веб-роуты с Jinja2
  - ✅ Все страницы HTTP 200
  - ✅ 20/20 тестов проходят

## Что осталось сделать (в порядке приоритета)

### M7: Frontend — дашборд и детальные страницы
- ⬜ Chart.js, Alpine.js, профили игроков, детали турниров

### M8: Frontend — фичи
- ⬜ Избранное, SSE, CSV, аутентификация на фронте

### M9: Telegram-bot
- ⬜ bot.py, handlers, api_client, notifier

### M10: Тестирование и CI
- ⬜ GitHub Actions, pre-commit hook

### M11: Финальная документация
- ⬜ README.md, финальная проверка

## Известные проблемы
- **bcrypt 5.x** несовместим с passlib 1.7.4 — зафиксирована версия 4.0.1
- **ruff** выдаёт ошибки в app/ (преимущественно в seed.py и моделях) — будут исправлены в M10 при настройке CI
- **Jinja2 3.1.x** несовместим со Starlette Jinja2Templates — используется кастомный Environment с cache_size=0

## Эволюция проектных решений
- **2026-06-06**: Инициализация
- **2026-06-06 13:35**: IMPLEMENTATION_PLAN, архитектурные решения
- **2026-06-06 14:17**: M2 завершён — Docker-инфраструктура
- **2026-06-06 14:38**: M3 завершён — модели, миграции, схемы, seed
- **2026-06-06 16:40**: M4 завершён — API: auth + CRUD + тесты 8/8
- **2026-06-06 16:58**: M5 завершён — API: специфичные фичи + тесты 20/20
- **2026-06-06 20:24**: M6 завершён — Frontend: шаблоны, CSS, JS, веб-роуты
- **2026-06-06 20:33**: Memory Bank расширен — созданы module-файлы для быстрого поиска информации агентом

## Ссылки на модули

Детальное описание каждого слоя — в соответствующих файлах:

- [Карта модулей](modules/overview.md)
- [Core: config, database, security](modules/core-layer.md)
- [Models: SQLAlchemy ORM](modules/models-layer.md)
- [Schemas: Pydantic DTO](modules/schemas-layer.md)
- [Services: business logic](modules/services-layer.md)
- [API: endpoints & routing](modules/api-layer.md)
- [Web: templates, CSS, JS](modules/web-layer.md)
- [Alembic: migrations](modules/alembic.md)
- [Testing: pytest suite](modules/testing.md)
- [Telegram bot](modules/telegram-bot.md)
- [Docker infrastructure](modules/docker-infra.md)