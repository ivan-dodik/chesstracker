# Chess Tracker

Full-stack приложение для отслеживания шахматных турниров, игроков и их рейтингов.

## Стек технологий

| Компонент | Технология |
|-----------|-----------|
| Backend | Python 3.12, FastAPI, Uvicorn |
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
| Зависимости | uv |

## Предварительные требования

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Git

## Быстрый старт

1. Клонировать репозиторий:

```bash
git clone git@github.com:ivan-dodik/chesstracker.git
cd chesstracker
```

2. Создать файл `.env` из шаблона:

```bash
cp .env.example .env
```

3. Запустить проект:

```bash
docker compose up --build
```

> При первом запуске автоматически выполняются миграции базы данных и заполняются тестовые данные (30 игроков, 10 турниров, 200+ партий).

4. Открыть в браузере:
   - **Веб-интерфейс**: http://localhost:8000
   - **Swagger UI**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc

## Переменные окружения

Основные переменные (полный список — в `.env.example`):

| Переменная | Описание | По умолчанию |
|-----------|----------|-------------|
| `DATABASE_URL` | Подключение к PostgreSQL | `postgresql+asyncpg://ct_user:ct_password@db:5432/ct_db` |
| `SECRET_KEY` | Ключ для JWT | `super-secret-key-change-in-production` |
| `TG_BOT_TOKEN` | Токен Telegram бота | (опционально) |
| `BACKEND_URL` | URL для доступа к API из telegram-bot | `http://backend:8000` |
| `DEBUG` | Режим отладки | `true` |

## Пользователи

| Роль | Username | Password |
|------|----------|----------|
| Администратор | `admin` | `admin123` |
| Пользователь | `user` | `user123` |

## API документация

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Основные эндпоинты

#### Аутентификация
- `POST /api/auth/login` — JWT логин
- `POST /api/auth/register` — создание пользователя (admin)
- `GET /api/auth/me` — текущий пользователь

#### Игроки
- `GET /api/players` — список с пагинацией и поиском
- `GET /api/players/{id}` — детальная информация
- `GET /api/players/{id}/rating-history` — история рейтинга

#### Турниры
- `GET /api/tournaments` — список с фильтрацией
- `GET /api/tournaments/{id}` — детальная информация
- `GET /api/tournaments/{id}/standings` — турнирная таблица
- `GET /api/tournaments/{id}/export/csv` — экспорт в CSV

#### Партии
- `GET /api/tournaments/{id}/games` — список партий турнира
- `POST /api/tournaments/{id}/import/csv` — импорт результатов из CSV

#### Статистика
- `GET /api/stats/top-rated` — топ-10 игроков
- `GET /api/stats/overall/{player_id}` — общая статистика игрока
- `GET /api/stats/head-to-head/{p1}/{p2}` — личные встречи

#### Избранное
- `GET /api/favorites` — избранные текущего пользователя
- `POST /api/favorites/{player_id}` — добавить в избранное
- `DELETE /api/favorites/{player_id}` — удалить из избранного

#### Прочее
- `GET /api/events` — SSE поток событий
- `GET /api/activity-log` — лог активности

### Web-страницы
- `GET /` — дашборд
- `GET /login` — страница входа
- `GET /players` — список игроков
- `GET /players/{id}` — профиль игрока
- `GET /tournaments` — список турниров
- `GET /tournaments/{id}` — страница турнира

## Команды для разработки

### Backend

```bash
cd backend

# Установка зависимостей
uv sync

# Запуск сервера (локально, без Docker)
uv run uvicorn app.main:app --reload --port 8000

# Запуск seed
uv run python -m app.seed

# Миграции
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "description"

# Линтинг
uv run ruff check .
uv run ruff format .

# Тесты
uv run pytest -v
```

### Telegram-bot

```bash
cd telegram-bot

# Установка зависимостей
uv sync

# Линтинг
uv run ruff check .
uv run ruff format .
```

### Docker

```bash
# Сборка и запуск всех сервисов
docker compose up --build

# Запуск в фоне
docker compose up -d

# Просмотр логов
docker compose logs -f

# Остановка
docker compose down

# Запуск seed в контейнере
docker compose run --rm backend python -m app.seed

# Запуск тестов в контейнере
docker compose run --rm backend pytest -v

# Сборка конкретного сервиса
docker compose build backend
docker compose build telegram-bot

# Очистка (с удалением томов БД)
docker compose down -v
```

## Структура проекта

```
chesstracker/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # REST и web-роуты
│   │   ├── core/              # config, database, security
│   │   ├── models/            # SQLAlchemy модели
│   │   ├── schemas/           # Pydantic схемы
│   │   ├── services/          # Бизнес-логика
│   │   ├── static/            # CSS, JS
│   │   ├── templates/         # Jinja2 шаблоны
│   │   ├── main.py            # Точка входа
│   │   └── seed.py            # Seed-данные
│   ├── alembic/               # Миграции
│   ├── entrypoint.sh          # Точка входа Docker (миграции + seed)
│   └── tests/                 # Тесты
├── telegram-bot/              # Telegram бот
│   ├── handlers/              # Обработчики команд
│   └── services/              # API-клиент и нотификатор
├── memory-bank/               # Документация Memory Bank
├── .github/workflows/         # CI конфигурация
├── docker-compose.yml         # Docker Compose
├── .env.example               # Шаблон переменных окружения
├── ARCHITECTURE.md            # Архитектура проекта
├── IMPLEMENTATION_PLAN.md     # План реализации
├── CHANGES.md                 # История изменений
├── PROMPTS.md                 # История промптов
└── REPORT.md                  # Отчёт по проекту
```

## Архитектура

Подробное описание архитектуры — в [ARCHITECTURE.md](ARCHITECTURE.md).

## Лицензия

GNU Affero General Public License v3.0 (AGPL-3.0-only)

Проект распространяется под лицензией AGPL-3.0, которая требует публикации исходного кода при использовании программного обеспечения по сети (SaaS clause).
