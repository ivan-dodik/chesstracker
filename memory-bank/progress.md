# Progress: Chess Tracker

## Текущий статус
**M8: Frontend — фичи** завершён. Добавлен SSE-клиент с toast-уведомлениями. Аутентификация, избранное, CSV импорт/экспорт реализованы в M7. 20/20 тестов проходят, docker build успешен.

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
- ✅ **M5: Backend — API: специфичные фичи**
- ✅ **M6: Frontend — базовая структура и навигация**
- ✅ **M7: Frontend — дашборд и детальные страницы**
  - ✅ Веб-роуты: /players/{id}, /tournaments/{id}
  - ✅ Chart.js CDN в base.html
  - ✅ Дашборд: графики рейтинга (line chart) и статистики (doughnut chart)
  - ✅ Профиль игрока: рейтинг, статистика wins/losses/draws, график, head-to-head, избранное
  - ✅ Детали турнира: standings, партии по турам (аккордеон), CSV экспорт/импорт
  - ✅ TournamentStandings: wins, draws, losses
  - ✅ GameRead: white_player_name, black_player_name
  - ✅ CSS для страниц игрока, турнира, графиков
  - ✅ 20/20 тестов проходят
- ✅ **M8: Frontend — фичи**
  - ✅ SSE-клиент (backend/app/static/js/sse.js): EventSource к /api/events, toast-уведомления
  - ✅ SSE-клиент подключён в base.html
  - ✅ CSS flash-warning стиль
  - ✅ Защита роутов: 401 → редирект на /login
  - ✅ Аутентификация на фронте: логин форма, JWT в localStorage, Authorization header
  - ✅ Избранное: кнопка ★ на профиле, список на дашборде
  - ✅ Экспорт CSV: кнопка на странице турнира
  - ✅ Импорт CSV: форма для админа на странице турнира

## Что осталось сделать (в порядке приоритета)

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
- **2026-06-06 20:58**: M7 завершён — дашборд с Chart.js, профили игроков, детали турниров
- **2026-06-06 21:06**: M8 завершён — SSE-клиент, toast-уведомления, CSS flash-warning; обновлены CHANGES.md, PROMPTS.md, REPORT.md, Memory Bank

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