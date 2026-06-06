# Архитектура Chess Tracker

## Обзор

Chess Tracker — full-stack приложение для отслеживания шахматных турниров, игроков и их рейтингов. Состоит из трёх сервисов, объединённых в Docker Compose.

## Архитектура системы

```
┌──────────────────────────────────────────────────────────┐
│                    Docker Compose                         │
│                                                           │
│  ┌─────────────────────┐    ┌──────────────────────────┐  │
│  │     Backend         │    │      Telegram-bot         │  │
│  │    (FastAPI)        │◄──►│   (python-telegram-bot)   │  │
│  │     :8000           │    │                           │  │
│  │                     │    │    Long-polling REST      │  │
│  │  Jinja2 + HTMX      │    │                           │  │
│  │  + Alpine.js        │    └──────────────────────────┘  │
│  └─────────┬───────────┘                                   │
│            │                                               │
│  ┌─────────┴───────────┐                                   │
│  │     PostgreSQL       │                                   │
│  │     :5432            │                                   │
│  └─────────────────────┘                                   │
└──────────────────────────────────────────────────────────┘
```

## Компоненты

### 1. Backend (FastAPI)

Серверная часть на Python, которая:
- Отдаёт REST API (JSON) для взаимодействия с БД
- Генерирует HTML-страницы через Jinja2 шаблоны
- Обрабатывает аутентификацию (JWT)
- Предоставляет Swagger UI по адресу `/docs`
- Рассылает SSE-события для real-time уведомлений

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Точка входа FastAPI
│   ├── api/                    # Роутеры
│   │   ├── __init__.py
│   │   ├── router.py           # Объединение всех роутеров
│   │   ├── deps.py             # Зависимости (get_db, get_current_user)
│   │   ├── auth.py             # POST /api/auth/login, register, me
│   │   ├── players.py          # CRUD /api/players
│   │   ├── tournaments.py      # CRUD /api/tournaments
│   │   ├── games.py            # CRUD /api/games
│   │   ├── ratings.py          # /api/players/{id}/rating-history
│   │   ├── favorites.py        # /api/favorites
│   │   ├── stats.py            # /api/stats/*
│   │   ├── sse.py              # /api/events (SSE)
│   │   ├── export.py           # /api/export/csv
│   │   ├── import_route.py     # /api/import/csv
│   │   ├── activity_log.py     # /api/activity-log
│   │   └── web.py              # HTML-роуты (/, /players, /tournaments, /login)
│   ├── core/                   # Конфигурация, БД, безопасность
│   │   ├── __init__.py
│   │   ├── config.py           # Pydantic BaseSettings
│   │   ├── database.py         # async engine, sessionmaker, get_db
│   │   └── security.py         # Hash, JWT
│   ├── models/                 # SQLAlchemy модели
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── player.py
│   │   ├── tournament.py
│   │   ├── game.py
│   │   ├── rating_history.py
│   │   ├── favorite.py
│   │   └── activity_log.py
│   ├── schemas/                # Pydantic схемы
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── player.py
│   │   ├── tournament.py
│   │   ├── game.py
│   │   ├── rating.py
│   │   ├── favorite.py
│   │   └── activity_log.py
│   ├── services/               # Бизнес-логика
│   │   ├── __init__.py
│   │   ├── player_service.py
│   │   ├── tournament_service.py
│   │   ├── game_service.py
│   │   ├── rating_service.py
│   │   ├── favorite_service.py
│   │   ├── stats_service.py
│   │   ├── sse_service.py
│   │   ├── export_service.py
│   │   ├── import_service.py
│   │   └── activity_log_service.py
│   ├── templates/              # Jinja2 шаблоны
│   │   ├── base.html
│   │   ├── index.html          # Дашборд
│   │   ├── login.html
│   │   ├── players/
│   │   │   ├── list.html
│   │   │   └── detail.html
│   │   ├── tournaments/
│   │   │   ├── list.html
│   │   │   └── detail.html
│   │   └── partials/
│   │       ├── player_row.html
│   │       ├── tournament_row.html
│   │       └── pagination.html
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       ├── main.js
│   │       └── sse.js
│   └── seed.py                 # Seed-данные
├── alembic/                    # Миграции
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_players.py
│   ├── test_ratings.py
│   ├── test_stats.py
│   └── test_favorites.py
├── pyproject.toml
└── Dockerfile
```

### 2. Telegram-bot

Отдельный микросервис для уведомлений:
- Long-polling (не webhook) — проще для локальной разработки
- Сам polling'ит backend через REST
- Команды: `/start`, `/subscribe`, `/unsubscribe`

```
telegram-bot/
├── bot.py
├── config.py
├── handlers/
│   ├── __init__.py
│   ├── start.py
│   └── subscribe.py
├── services/
│   ├── __init__.py
│   ├── api_client.py
│   └── notifier.py
├── pyproject.toml
└── Dockerfile
```

### 3. PostgreSQL 16

Хранит все данные приложения. Используется async драйвер asyncpg.

## Модели данных (ERD)

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│    User      │     │    Favorite      │     │   Player     │
├──────────────┤     ├──────────────────┤     ├──────────────┤
│ id (PK)      │1──N │ id (PK)          │N──1 │ id (PK)      │
│ username     │     │ user_id (FK)     │     │ name         │
│ hashed_pass  │     │ player_id (FK)   │     │ rating       │
│ role         │     │ created_at       │     │ city         │
│ created_at   │     │ UNIQUE(user,     │     │ avatar_url   │
└──────────────┘     │       player)    │     │ created_at   │
                     └──────────────────┘     │ updated_at   │
                                              └──────┬───────┘
               ┌───────────────┐                     │
               │ RatingHistory │                     │
               ├───────────────┤                     │
               │ id (PK)       │                     │
               │ player_id (FK)│N────────────────────1│
               │ rating        │                     │
               │ date          │                     │
               │ tournament_id │                     │
               └───────────────┘                     │
               ┌───────────────┐                     │
               │     Game      │                     │
               ├───────────────┤                     │
               │ id (PK)       │                     │
               │ tournament_id │                     │
               │ round         │                     │
               │ white_player  │N────────────────────1│ (white)
               │ black_player  │N────────────────────1│ (black)
               │ result        │                     │
               │ played_at     │                     │
               │ created_at    │                     │
               └───────┬───────┘                     │
                       │                             │
              ┌────────┴────────┐                    │
              │  Tournament     │                    │
              ├─────────────────┤                    │
              │ id (PK)         │                    │
              │ name            │                    │
              │ start_date      │                    │
              │ end_date        │                    │
              │ location        │                    │
              │ rounds          │                    │
              │ type            │                    │
              │ status          │                    │
              │ created_at      │                    │
              │ updated_at      │                    │
              └─────────────────┘                    │
                                                     │
              ┌──────────────────┐                   │
              │  ActivityLog     │                   │
              ├──────────────────┤                   │
              │ id (PK)          │                   │
              │ user_id (FK)     │                   │
              │ action           │                   │
              │ entity_type      │                   │
              │ entity_id        │                   │
              │ old_values (JSON)│                   │
              │ new_values (JSON)│                   │
              │ timestamp        │                   │
              └──────────────────┘                   │
```

## API Endpoints

### REST API (JSON)

#### Аутентификация
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/auth/login` | JWT логин (username + password) |
| POST | `/api/auth/register` | Создание пользователя (admin only) |
| GET | `/api/auth/me` | Текущий пользователь |

#### Игроки
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/players` | Список с пагинацией, поиском |
| POST | `/api/players` | Создание (admin only) |
| GET | `/api/players/{id}` | Детальная информация |
| PUT | `/api/players/{id}` | Обновление (admin only) |
| DELETE | `/api/players/{id}` | Удаление (admin only) |
| GET | `/api/players/{id}/rating-history` | История рейтинга |

#### Турниры
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/tournaments` | Список с пагинацией, фильтрацией |
| POST | `/api/tournaments` | Создание (admin only) |
| GET | `/api/tournaments/{id}` | Детальная информация |
| PUT | `/api/tournaments/{id}` | Обновление (admin only) |
| DELETE | `/api/tournaments/{id}` | Удаление (admin only) |
| GET | `/api/tournaments/{id}/standings` | Турнирная таблица |
| GET | `/api/tournaments/{id}/export/csv` | Экспорт в CSV |

#### Партии
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/tournaments/{id}/games` | Список партий турнира |
| POST | `/api/tournaments/{id}/games` | Добавление партии (admin only) |
| PUT | `/api/games/{id}` | Обновление результата (admin only) |
| DELETE | `/api/games/{id}` | Удаление партии (admin only) |

#### Статистика
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/stats/head-to-head/{p1}/{p2}` | Личные встречи |
| GET | `/api/stats/top-rated` | Топ-10 игроков |
| GET | `/api/stats/overall/{player_id}` | Общая статистика |

#### Избранное
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/favorites` | Избранные текущего пользователя |
| POST | `/api/favorites/{player_id}` | Добавить в избранное |
| DELETE | `/api/favorites/{player_id}` | Удалить из избранного |

#### Прочее
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/events` | SSE поток событий |
| POST | `/api/tournaments/{id}/import/csv` | Импорт результатов из CSV |
| GET | `/api/activity-log` | Лог активности |

### Web Routes (HTML)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/` | Дашборд |
| GET | `/players` | Список игроков |
| GET | `/players/{id}` | Профиль игрока |
| GET | `/tournaments` | Список турниров |
| GET | `/tournaments/{id}` | Страница турнира |
| GET | `/login` | Страница входа |

## Стек технологий

| Компонент | Технология |
|-----------|-----------|
| Backend | Python 3.12+, FastAPI, Uvicorn |
| Database | PostgreSQL 16, asyncpg |
| ORM | SQLAlchemy 2.0 (asyncio) |
| Миграции | Alembic |
| Валидация | Pydantic v2 |
| Аутентификация | JWT (python-jose), bcrypt (passlib) |
| Frontend | Jinja2 + HTMX + Alpine.js + Chart.js |
| Telegram-bot | python-telegram-bot |
| Линтер | ruff |
| CI | GitHub Actions |
| Контейнеризация | Docker, Docker Compose |

## План разработки

Подробный план реализации — в [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md).

### Майлстоуны

1. **M1**: Архитектура и планирование — создание документации
2. **M2**: Окружение и Docker — Dockerfile, docker-compose, структура директорий
3. **M3**: Модели и БД — SQLAlchemy модели, Alembic, seed-данные
4. **M4**: API — аутентификация и базовые CRUD
5. **M5**: API — специфичные фичи (рейтинг, статистика, SSE, CSV, лог)
6. **M6**: Frontend — базовая структура и навигация (Jinja2, HTMX)
7. **M7**: Frontend — дашборд и детальные страницы (Chart.js)
8. **M8**: Frontend — фичи (избранное, SSE, CSV, аутентификация)
9. **M9**: Telegram-bot — уведомления
10. **M10**: Тестирование и CI — GitHub Actions, ruff, pytest
11. **M11**: Финальная документация

## Ключевые архитектурные решения

1. **Монорепозиторий** — все компоненты в одном репозитории
2. **Frontend как часть backend** — Jinja2 шаблоны отдаются FastAPI, без отдельного сервера
3. **Микросервис для Telegram-bot** — отдельный контейнер, long-polling по REST
4. **SSE вместо WebSocket** — для простых уведомлений не нужен WebSocket
5. **JWT аутентификация** — два предзаполненных аккаунта (admin, user)
6. **Управление зависимостями — `uv`** (не pip/poetry)
7. **Линтер — `ruff`** (flake8 + isort + pyupgrade в одном)