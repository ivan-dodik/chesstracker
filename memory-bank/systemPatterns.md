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
│   │   ├── players.py    # CRUD игроков
│   │   ├── tournaments.py # CRUD турниров
│   │   ├── games.py      # CRUD партий
│   │   ├── ratings.py    # Рейтинговая история
│   │   ├── favorites.py  # Избранные игроки
│   │   ├── stats.py      # Статистика
│   │   ├── export.py     # CSV экспорт/импорт
│   │   └── sse.py        # Server-Sent Events
│   ├── models/           # SQLAlchemy модели
│   ├── schemas/          # Pydantic схемы
│   ├── services/         # Бизнес-логика
│   ├── templates/        # Jinja2 шаблоны
│   ├── static/           # CSS, JS (Alpine.js, Chart.js)
│   ├── core/             # Config, database, security
│   └── main.py           # Точка входа
├── alembic/              # Миграции
├── tests/                # Тесты
├── pyproject.toml
└── Dockerfile
```

### Frontend (встроен в backend)
- Jinja2 шаблоны в `backend/app/templates/`
- HTMX для динамической загрузки контента (атрибуты hx-*)
- Alpine.js для реактивности на клиенте (x-data, x-init, и т.д.)
- Chart.js для графиков на дашборде
- Никакого отдельного frontend-сервера

### Telegram-bot (отдельный микросервис)
```
telegram-bot/
├── bot.py                # Точка входа
├── handlers/             # Обработчики команд
├── services/             # HTTP-клиент к backend
├── pyproject.toml
└── Dockerfile
```

## Ключевые архитектурные решения

1. **Монорепозиторий**: один репозиторий для всех компонентов
2. **Frontend как часть backend**: шаблоны Jinja2 отдаются FastAPI, без отдельного сервера
3. **Микросервис для Telegram-bot**: отдельный контейнер, общается с backend по HTTP
4. **SSE вместо WebSocket**: для простых уведомлений не нужен WebSocket
5. **JWT аутентификация**: два предзаполненных аккаунта (admin, user)

## Паттерны проектирования

### Repository Pattern
- SQLAlchemy модели инкапсулируют доступ к данным
- Services содержат бизнес-логику
- API роутеры обрабатывают HTTP и вызывают services

### Dependency Injection (FastAPI)
- Сессии БД через Depends(get_db)
- Текущий пользователь через Depends(get_current_user)

### DTO (Pydantic schemas)
- Валидация входящих данных
- Сериализация ответов

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
- `GET /api/events` — SSE поток

### Web routes (HTML via HTMX)
- `GET /` — дашборд
- `GET /players` — список игроков
- `GET /players/{id}` — профиль игрока
- `GET /tournaments` — список турниров
- `GET /tournaments/{id}` — страница турнира
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

- [Overview & dependency graph](modules/overview.md)
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