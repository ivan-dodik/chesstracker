# System Patterns: Chess Tracker

## Архитектура

```
┌─────────────────────────────────────────────────────┐
│                   Docker Compose                     │
│                                                      │
│  ┌──────────────┐    ┌──────────────┐               │
│  │   Backend     │    │ Telegram-bot │               │
│  │  (FastAPI)    │◄──►│  (python-    │               │
│  │  :8000        │    │  telegram-   │               │
│  │               │    │  bot)        │               │
│  └──────┬───────┘    └──────────────┘               │
│         │                                            │
│  ┌──────┴───────┐                                    │
│  │  PostgreSQL   │                                    │
│  │  :5432        │                                    │
│  └──────────────┘                                    │
└─────────────────────────────────────────────────────┘
```

## Компонентная архитектура

### Backend (FastAPI)
```
backend/
├── app/
│   ├── api/              # Роутеры FastAPI
│   │   ├── auth.py       # Аутентификация (JWT)
│   │   ├── deps.py       # get_db, get_current_user, get_current_user_for_web
│   │   ├── players.py    # CRUD игроков
│   │   ├── tournaments.py # CRUD турниров
│   │   ├── games.py      # CRUD партий
│   │   ├── ratings.py    # Рейтинговая история
│   │   ├── favorites.py  # Избранные игроки
│   │   ├── stats.py      # Статистика
│   │   ├── export.py     # CSV экспорт/импорт
│   │   ├── import_route.py # Импорт CSV
│   │   ├── activity_log.py # Лог активности
│   │   ├── sse.py        # Server-Sent Events
│   │   └── web.py        # Веб-роуты (HTML через Jinja2)
│   ├── models/           # SQLAlchemy модели (7 моделей)
│   ├── schemas/          # Pydantic схемы
│   ├── services/         # Бизнес-логика
│   │   ├── activity_log_service.py
│   │   ├── export_service.py
│   │   ├── favorite_service.py
│   │   └── ...
│   ├── templates/        # Jinja2 шаблоны (17 шаблонов + partials)
│   ├── static/           # CSS, JS (Alpine.js, ApexCharts, SSE client)
│   ├── core/             # Config, database, security
│   │   ├── config.py     # Pydantic BaseSettings
│   │   ├── database.py   # async engine + session
│   │   └── security.py   # JWT + bcrypt
│   ├── middleware/        # TimingMiddleware + HealthCheckFilter
│   └── main.py           # FastAPI app + lifespan (pool warmup, rate limiting, file logging)
├── alembic/              # Миграции
├── tests/                # API + service тесты
├── e2e/                  # E2E тесты (Playwright)
├── entrypoint.sh         # Docker entrypoint (миграции + seed)
├── Dockerfile
└── pyproject.toml
```

### Frontend (встроен в backend)
- Jinja2 шаблоны в `backend/app/templates/`
- HTMX для динамической загрузки контента (hx-boost, hx-get, hx-post, hx-swap)
- Alpine.js для реактивности на клиенте (x-data, x-init)
- ApexCharts для графиков на дашборде и странице игрока
- SSE клиент (`sse.js`) для real-time уведомлений (toast)
- Никакого отдельного frontend-сервера
- **hx-boost + Alpine.js**: скрипты в `{% block content %}`, `Alpine.initTree()` в `htmx:afterSwap`

### Telegram-bot (отдельный микросервис)
```
telegram-bot/
├── bot.py                # Точка входа
├── config.py             # Pydantic BaseSettings
├── handlers/             # Обработчики команд (/start, /subscribe, /unsubscribe)
├── services/             # HTTP-клиент к backend + notifier
├── tests/                # Тесты (api_client, notifier)
├── Dockerfile
└── pyproject.toml
```

## Ключевые архитектурные решения

1. **Монорепозиторий**: один репозиторий для всех компонентов
2. **Frontend как часть backend**: шаблоны Jinja2 отдаются FastAPI, без отдельного сервера
3. **Микросервис для Telegram-bot**: отдельный контейнер, общается с backend по HTTP
4. **SSE вместо WebSocket**: для простых уведомлений не нужен WebSocket
5. **JWT аутентификация**: два предзаполненных аккаунта (admin, user), cookie jwt_token для веб-страниц, rate limiting через slowapi
6. **lazy="raise" на моделях**: предотвращает N+1; явный selectinload() в сервисах
7. **entrypoint.sh**: Docker entrypoint для автоматических миграций и seed

## Паттерны проектирования

### Repository Pattern
- SQLAlchemy модели инкапсулируют доступ к данным
- Services содержат бизнес-логику
- API роутеры обрабатывают HTTP и вызывают services

### Dependency Injection (FastAPI)
- Сессии БД через Depends(get_db)
- Текущий пользователь через Depends(get_current_user) или Depends(get_current_user_for_web) для веб-страниц

### DTO (Pydantic schemas)
- Валидация входящих данных
- Сериализация ответов

### HTMX + Alpine.js Integration
- `hx-boost="true"` на `<body>` для AJAX-навигации
- `htmx:afterSwap` → `Alpine.initTree()` для re-init Alpine.js компонентов
- `this._initialized` guard от двойной инициализации
- `Promise.all()` для параллельных fetch-запросов

## Модели данных (SQLAlchemy)

Основные сущности:
- **User**: id, username, hashed_password, role (admin/user)
- **Player**: id, name, rating, city, avatar_url, created_at
- **Tournament**: id, name, start_date, end_date, location, rounds, type (classic/blitz/rapid), status (active/completed)
- **Game**: id, tournament_id, round, white_player_id, black_player_id, result (1-0/0-1/½-½), played_at
- **RatingHistory**: id, player_id, rating, date, tournament_id
- **Favorite**: id, user_id, player_id
- **ActivityLog**: id, user_id, action, entity_type, entity_id, old_values, new_values, timestamp

## Маршруты (API endpoints)

### API routes (JSON)
- `POST /api/auth/login` — JWT логин
- `POST /api/auth/register` — регистрация (admin only)
- `GET /api/auth/me` — текущий пользователь
- `GET/POST /api/players` — список/создание игроков
- `GET/PUT/DELETE /api/players/{id}` — CRUD игрока
- `GET /api/players/{id}/rating-history` — история рейтинга
- `GET /api/players/{id}/tournaments` — турниры игрока
- `GET/POST /api/tournaments` — список/создание турниров
- `GET/PUT/DELETE /api/tournaments/{id}` — CRUD турнира
- `GET /api/tournaments/{id}/standings` — турнирная таблица
- `GET/POST /api/tournaments/{id}/games` — партии турнира
- `GET /api/stats/head-to-head/{p1}/{p2}` — личные встречи
- `GET /api/stats/top-rated` — топ-10 игроков
- `POST /api/export/tournament/{id}/csv` — экспорт CSV
- `POST /api/import/tournament/{id}/csv` — импорт CSV
- `GET /api/favorites` — избранные текущего пользователя
- `GET /api/activity-log` — лог активности (admin only)
- `GET /api/events` — SSE поток

### Web routes (HTML via HTMX)
- `GET /` — дашборд
- `GET /players` — список игроков
- `GET /players/create` — создание игрока (admin)
- `GET /players/{id}` — профиль игрока
- `GET /players/{id}/edit` — редактирование игрока (admin)
- `GET /tournaments` — список турниров
- `GET /tournaments/create` — создание турнира (admin)
- `GET /tournaments/{id}` — страница турнира
- `GET /tournaments/{id}/edit` — редактирование турнира (admin)
- `GET /games/{id}/edit` — редактирование партии (admin)
- `GET /login` — страница входа

## ERD (Entity Relationship Diagram)

```
User 1──N Favorite N──1 Player
Player 1──N RatingHistory
Tournament 1──N Game N──2 Player (white/black)
User 1──N ActivityLog
```

## Ссылки на модули

Подробное описание каждого слоя:

- [Overview & dependency graph](backend/overview.md)
- [Core: config, database, security](backend/core-layer.md)
- [Models: SQLAlchemy ORM](backend/models-layer.md)
- [Schemas: Pydantic DTO](backend/schemas-layer.md)
- [Services: business logic](backend/services-layer.md)
- [API: endpoints & routing](backend/api-layer.md)
- [Web: templates, CSS, JS](backend/web-layer.md)
- [Alembic: migrations](backend/alembic.md)
- [Testing: pytest suite](testing/overview.md)
- [Telegram bot](telegram-bot/overview.md)
- [Docker infrastructure](infrastructure/docker.md)