# Implementation Plan: Chess Tracker

## Общие правила

1. **Перед началом работы** — прочитать этот файл.
2. **Каждый tool use** — обновлять `task_progress` с текущим состоянием чекмаков.
3. **После каждого шага** (или группы связанных шагов):
   - Обновить `CHANGES.md`
   - Обновить `PROMPTS.md` (если был новый промпт)
   - Обновить `REPORT.md` (добавить запись в «Историю работы»)
4. **После каждого майлстоуна** (M1–M11):
   - Выполнить коммит + пуш (согласно `.clinerules/git_commit.md`)
   - Обновить Memory Bank (activeContext.md, progress.md, при необходимости другие файлы)
5. **Pre-commit hook**: настроить ruff для автоматического форматирования при коммите.

---

## Майлстоуны

### M1: Архитектура и планирование
**Коммит:** `docs: add architecture documentation and implementation plan`

- [ ] Создать `ARCHITECTURE.md`:
  - Описание архитектуры (текст + диаграмма из systemPatterns.md)
  - ERD (из systemPatterns.md)
  - План разработки (ссылка на IMPLEMENTATION_PLAN.md)
  - Стек технологий
  - Структура директорий
- [ ] Убедиться, что `IMPLEMENTATION_PLAN.md` (этот файл) содержит все актуальные чекмаки
- [ ] Создать `REPORT.md` — начальная структура отчёта (AI-инструменты, примеры промптов, ключевые проблемы и решения, удачные/неудачные шаги, история работы за M1)
- [ ] Обновить Memory Bank (activeContext.md, progress.md)

### M2: Окружение и Docker
**Коммит:** `chore: setup docker environment and project scaffolding`

- [ ] Обновить `CHANGES.md`, `PROMPTS.md`, `REPORT.md` — зафиксировать изменения, промпты и историю работы по M2
- [ ] Обновить `REPORT.md` — добавить запись в «Историю работы» о шагах M2, зафиксировать проблемы/решения

- [ ] Создать `backend/pyproject.toml` через `uv init`:
  - Зависимости: fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, alembic, pydantic-settings, python-jose[cryptography], passlib[bcrypt], python-multipart, httpx, jinja2, aiofiles, sse-starlette
  - Dev-зависимости: pytest, pytest-asyncio, httpx, ruff
  - Конфигурация ruff
- [ ] Создать `backend/Dockerfile`:
  - FROM python:3.12-slim
  - Установка uv
  - Копирование pyproject.toml, uv.lock
  - `uv sync`
  - Копирование кода
  - CMD: uvicorn app.main:app --host 0.0.0.0 --port 8000
- [ ] Создать `telegram-bot/pyproject.toml`:
  - Зависимости: python-telegram-bot, httpx, pydantic-settings
  - Dev-зависимости: ruff
- [ ] Создать `telegram-bot/Dockerfile`:
  - FROM python:3.12-slim
  - Аналогично backend, CMD: python bot.py
- [ ] Создать `.env.example`:
  - DATABASE_URL, SECRET_KEY, TG_BOT_TOKEN, и т.д.
- [ ] Создать `docker-compose.yml`:
  - **db**: postgres:16, volume, env, healthcheck
  - **backend**: build: ./backend, depends_on: db, ports: 8000:8000, env_file
  - **telegram-bot**: build: ./telegram-bot, depends_on: backend, env_file
- [ ] Создать `docker-compose.override.yml` для разработки:
  - backend: volumes для hot-reload, ports
  - db: ports 5432:5432
- [ ] Создать `postgres-init/init.sql` — создание БД и пользователя (optional, можно через POSTGRES_* env)
- [ ] Создать структуру директорий backend:
  - `backend/app/__init__.py`
  - `backend/app/core/`
  - `backend/app/models/`
  - `backend/app/schemas/`
  - `backend/app/api/`
  - `backend/app/services/`
  - `backend/app/templates/`
  - `backend/app/static/css/`
  - `backend/app/static/js/`
  - `backend/tests/`
- [ ] Проверить: `docker compose build` успешен
- [ ] Обновить Memory Bank

### M3: Backend — модели и база данных
**Коммит:** `feat: add SQLAlchemy models and initial migration`

- [ ] Обновить `CHANGES.md`, `PROMPTS.md`, `REPORT.md` — зафиксировать изменения, промпты и историю работы по M3

- [ ] Создать `backend/app/core/config.py`:
  - Pydantic BaseSettings: DATABASE_URL, SECRET_KEY, TG_BOT_TOKEN, DEBUG, и т.д.
- [ ] Создать `backend/app/core/database.py`:
  - async engine, async sessionmaker, async get_db dependency
- [ ] Создать `backend/app/core/security.py`:
  - hash_password(), verify_password() — passlib bcrypt
  - create_access_token(), decode_access_token() — python-jose JWT
- [ ] Создать модели SQLAlchemy в `backend/app/models/`:
  - **User**: id, username, hashed_password, role (admin/user), created_at
  - **Player**: id, name, rating, city, avatar_url, created_at, updated_at
  - **Tournament**: id, name, start_date, end_date, location, rounds, type (classic/blitz/rapid), status (active/completed), created_at, updated_at
  - **Game**: id, tournament_id (FK), round, white_player_id (FK), black_player_id (FK), result (1-0/0-1/½-½), played_at, created_at
  - **RatingHistory**: id, player_id (FK), rating, date, tournament_id (FK nullable)
  - **Favorite**: id, user_id (FK), player_id (FK), created_at (unique constraint user+player)
  - **ActivityLog**: id, user_id (FK), action, entity_type, entity_id, old_values (JSON), new_values (JSON), timestamp
- [ ] Создать `backend/app/models/__init__.py` — re-export всех моделей, Base
- [ ] Инициализировать Alembic: `alembic init alembic` внутри backend/
- [ ] Настроить `alembic/env.py` — подключение к DATABASE_URL, import моделей
- [ ] Создать первую миграцию: `alembic revision --autogenerate -m "initial"`
- [ ] Накатить миграцию: `alembic upgrade head`
- [ ] Создать `backend/app/seed.py`:
  - 2 пользователя (admin/admin123, user/user123)
  - 5 турниров (3 completed, 2 active)
  - 30+ игроков с рейтингами
  - 200+ партий
  - 50+ записей RatingHistory
  - Несколько Favorite записей
- [ ] Создать Pydantic схемы в `backend/app/schemas/`:
  - UserCreate, UserRead, Token
  - PlayerCreate, PlayerRead, PlayerList
  - TournamentCreate, TournamentRead, TournamentList, TournamentStandings
  - GameCreate, GameRead, GameResult
  - RatingHistoryRead
  - FavoriteRead
  - ActivityLogRead
- [ ] Проверить seed: запустить скрипт через `docker compose run --rm backend python -m app.seed`
- [ ] Обновить Memory Bank

### M4: Backend — API: аутентификация и базовые CRUD
**Коммит:** `feat: implement auth and basic CRUD API`

- [ ] Обновить `CHANGES.md`, `PROMPTS.md`, `REPORT.md` — зафиксировать изменения, промпты и историю работы по M4

- [ ] Создать `backend/app/api/deps.py`:
  - `get_db` — async session
  - `get_current_user` — JWT из Authorization header
  - `get_current_admin` — проверка роли admin
- [ ] Создать `backend/app/api/auth.py`:
  - `POST /api/auth/login` — username + password → JWT
  - `POST /api/auth/register` — создание нового пользователя (admin only)
  - `GET /api/auth/me` — текущий пользователь
- [ ] Создать `backend/app/services/player_service.py` + `backend/app/api/players.py`:
  - `GET /api/players` — список с пагинацией (page, per_page), поиском (name, rating, city)
  - `POST /api/players` — создание (admin only)
  - `GET /api/players/{id}` — детальная информация
  - `PUT /api/players/{id}` — обновление (admin only)
  - `DELETE /api/players/{id}` — удаление (admin only)
- [ ] Создать `backend/app/services/tournament_service.py` + `backend/app/api/tournaments.py`:
  - `GET /api/tournaments` — список с пагинацией, фильтрацией (date, location, status)
  - `POST /api/tournaments` — создание (admin only)
  - `GET /api/tournaments/{id}` — детальная информация
  - `PUT /api/tournaments/{id}` — обновление (admin only)
  - `DELETE /api/tournaments/{id}` — удаление (admin only)
- [ ] Создать `backend/app/services/game_service.py` + `backend/app/api/games.py`:
  - `GET /api/tournaments/{id}/games` — список партий турнира (с пагинацией по турам)
  - `POST /api/tournaments/{id}/games` — добавление партии (admin only)
  - `PUT /api/games/{id}` — обновление результата (admin only)
  - `DELETE /api/games/{id}` — удаление (admin only)
  - Автоматический подсчёт очков для турнирной таблицы
  - `GET /api/tournaments/{id}/standings` — турнирная таблица (сортировка по очкам)
- [ ] Создать `backend/app/api/router.py` — объединение всех роутеров в api_router
- [ ] Создать `backend/app/main.py`:
  - FastAPI app с lifespan (создание таблиц через alembic upgrade или проверка)
  - Подключение api_router
  - Монтирование static files
  - Настройка Jinja2Templates
  - CORS middleware
  - Swagger UI по /docs
- [ ] Написать тесты (3–4): `backend/tests/test_auth.py`, `backend/tests/test_players.py`
- [ ] Проверить Swagger UI: открыть /docs, протестировать эндпоинты
- [ ] Обновить Memory Bank

### M5: Backend — API: специфичные фичи
**Коммит:** `feat: add ratings, stats, favorites, SSE, CSV, activity log`

- [ ] Обновить `CHANGES.md`, `PROMPTS.md`, `REPORT.md` — зафиксировать изменения, промпты и историю работы по M5

- [ ] Создать `backend/app/services/rating_service.py` + `backend/app/api/ratings.py`:
  - `GET /api/players/{id}/rating-history` — история рейтинга с фильтром по дате
- [ ] Создать `backend/app/services/favorite_service.py` + `backend/app/api/favorites.py`:
  - `GET /api/favorites` — избранные текущего пользователя
  - `POST /api/favorites/{player_id}` — добавить в избранное
  - `DELETE /api/favorites/{player_id}` — удалить из избранного
- [ ] Создать `backend/app/services/stats_service.py` + `backend/app/api/stats.py`:
  - `GET /api/stats/head-to-head/{player1_id}/{player2_id}` — личные встречи
  - `GET /api/stats/top-rated` — топ-10 по рейтингу
  - `GET /api/stats/overall/{player_id}` — общая статистика (победы/ничьи/поражения)
- [ ] Создать `backend/app/services/sse_service.py` + `backend/app/api/sse.py`:
  - `GET /api/events` — SSE endpoint (подписка на события)
  - Отправка событий при: создании партии, изменении результата, изменении рейтинга
- [ ] Создать `backend/app/services/export_service.py` + `backend/app/api/export.py`:
  - `GET /api/tournaments/{id}/export/csv` — экспорт турнирной таблицы в CSV
- [ ] Создать `backend/app/services/import_service.py` + `backend/app/api/import_route.py`:
  - `POST /api/tournaments/{id}/import/csv` — импорт результатов из CSV (маппинг колонок: игрок, тур, соперник, результат)
- [ ] Создать `backend/app/services/activity_log_service.py` + `backend/app/api/activity_log.py`:
  - `GET /api/activity-log` — лог активности с пагинацией
  - Интегрировать логирование во все CRUD-операции (создание/редактирование/удаление)
- [ ] Написать тесты (3–4): `backend/tests/test_ratings.py`, `backend/tests/test_stats.py`, `backend/tests/test_favorites.py`
- [ ] Обновить Memory Bank

### M6: Frontend — базовая структура и навигация
**Коммит:** `feat: add base frontend with Jinja2 templates and HTMX`

- [ ] Обновить `CHANGES.md`, `PROMPTS.md`, `REPORT.md` — зафиксировать изменения, промпты и историю работы по M6

- [ ] Создать `backend/app/static/css/style.css`:
  - Адаптивная вёрстка (desktop + mobile)
  - CSS custom properties для темизации
  - Стили для навигации, таблиц, форм, карточек
- [ ] Создать `backend/app/static/js/main.js`:
  - Базовые Alpine.js компоненты
  - HTMX инициализация
- [ ] Создать `backend/app/templates/base.html`:
  - DOCTYPE html, head (meta viewport, title, CSS, JS)
  - Навигация (логотип, ссылки: дашборд, игроки, турниры; логин/логаут)
  - Блок для flash-сообщений
  - Блок content
  - Footer
  - Подключение: htmx.org, alpine.js, chart.js (CDN или локально)
- [ ] Создать `backend/app/templates/login.html`:
  - Форма логина (username, password)
  - HTMX: отправка формы → получение JWT → сохранение в localStorage
- [ ] Создать web-роуты в `backend/app/api/web.py`:
  - `GET /` — дашборд (index.html)
  - `GET /players` — список игроков (players/list.html)
  - `GET /tournaments` — список турниров (tournaments/list.html)
  - `GET /login` — страница входа
  - (детальные страницы — в M7)
- [ ] Создать `backend/app/templates/index.html` (каркас дашборда):
  - Разделы: топ-10 игроков, последние результаты, избранные (заглушки)
- [ ] Создать `backend/app/templates/players/list.html`:
  - Таблица игроков с HTMX-пагинацией
  - Поле поиска по имени (hx-trigger: keyup changed delay:500ms)
- [ ] Создать `backend/app/templates/tournaments/list.html`:
  - Таблица турниров с HTMX-пагинацией
  - Фильтры: статус, дата
- [ ] Создать HTMX-фрагменты: `backend/app/templates/partials/`:
  - `player_row.html` — строка таблицы игрока
  - `tournament_row.html` — строка таблицы турнира
  - `pagination.html` — компонент пагинации
- [ ] Проверить, что все страницы открываются (дашборд, списки, логин)
- [ ] Обновить Memory Bank

### M7: Frontend — дашборд и детальные страницы
**Коммит:** `feat: add dashboard with Chart.js and detail pages`

- [ ] Обновить `CHANGES.md`, `PROMPTS.md`, `REPORT.md` — зафиксировать изменения, промпты и историю работы по M7

- [ ] Реализовать дашборд (`templates/index.html`):
  - График рейтинга топ-игрока (Chart.js, line chart) — `GET /api/players/{id}/rating-history`
  - Круговая диаграмма результатов (Chart.js, doughnut) — `GET /api/stats/overall/{id}`
  - Топ-10 игроков (список) — `GET /api/stats/top-rated`
  - Избранные игроки (список с последними результатами)
- [ ] Создать `backend/app/templates/players/detail.html`:
  - Профиль игрока: имя, рейтинг, город, аватар
  - График истории рейтинга (Chart.js)
  - Список сыгранных турниров с результатами
  - Общая статистика (победы/ничьи/поражения)
  - Head-to-head с другим игроком (выпадающий список)
- [ ] Создать `backend/app/templates/tournaments/detail.html`:
  - Информация о турнире: название, даты, место, тип, статус
  - Турнирная таблица (таблица с очками, сортировка)
  - Партии по турам (аккордеон/табы)
  - Кнопка экспорта CSV
  - Форма импорта CSV (для админа)
- [ ] Создать Alpine.js компоненты:
  - Фильтры для списков (x-data, x-model)
  - Формы создания/редактирования (x-show для модалок)
  - Head-to-head селектор
- [ ] Создать дополнительный CSS для компонентов дашборда
- [ ] Проверить адаптивную вёрстку на мобильном разрешении (Chrome DevTools)
- [ ] Обновить Memory Bank

### M8: Frontend — фичи (избранное, SSE, CSV, аутентификация)
**Коммит:** `feat: add favorites UI, SSE client, CSV import/export, auth UI`

- [ ] Обновить `CHANGES.md`, `PROMPTS.md`, `REPORT.md` — зафиксировать изменения, промпты и историю работы по M8

- [ ] Реализовать избранное на фронте:
  - Кнопка "★" на профиле игрока (Alpine.js, hx-post/hx-delete)
  - Список избранных на дашборде
- [ ] Реализовать SSE-клиент:
  - `backend/app/static/js/sse.js` — EventSource подключение к `/api/events`
  - Toast-уведомления при новых событиях
- [ ] Реализовать экспорт CSV:
  - Кнопка "Экспорт CSV" на странице турнира → `GET /api/tournaments/{id}/export/csv` → скачивание
- [ ] Реализовать импорт CSV:
  - Форма загрузки файла на странице турнира (для админа)
  - HTMX: hx-encoding="multipart/form-data"
- [ ] Реализовать аутентификацию на фронте:
  - Форма логина → POST /api/auth/login → сохранение JWT в localStorage
  - HTMX: добавление Authorization header через hx-headers или Alpine.js
  - Защита роутов: перенаправление на /login если нет токена
  - Индикация: показать username в навигации, кнопка logout
- [ ] Проверить полный user flow:
  - Неавторизованный: просмотр дашборда, списков, профилей
  - Авторизованный (user): избранное, уведомления
  - Админ: создание/редактирование турниров, партий, импорт CSV
- [ ] Обновить Memory Bank

### M9: Telegram-bot
**Коммит:** `feat: add Telegram bot for notifications`

- [ ] Обновить `CHANGES.md`, `PROMPTS.md`, `REPORT.md` — зафиксировать изменения, промпты и историю работы по M9

- [ ] Создать `telegram-bot/bot.py`:
  - Инициализация Application (python-telegram-bot)
  - Регистрация обработчиков команд
  - Запуск long-polling: `application.run_polling()`
- [ ] Создать `telegram-bot/handlers/start.py`:
  - `/start` — приветственное сообщение, инструкция
- [ ] Создать `telegram-bot/handlers/subscribe.py`:
  - `/subscribe` — подписка на уведомления (сохраняет chat_id)
  - `/unsubscribe` — отписка
- [ ] Создать `telegram-bot/services/api_client.py`:
  - HTTP-клиент (httpx.AsyncClient) для запросов к backend
  - GET /api/tournaments/active — получить активные турниры
  - GET /api/tournaments/{id}/games/latest — получить последние результаты
- [ ] Создать `telegram-bot/services/notifier.py`:
  - Периодическая проверка новых результатов (каждые N секунд)
  - Отправка уведомлений подписанным пользователям
- [ ] Настроить конфигурацию: `telegram-bot/config.py` (pydantic-settings):
  - TG_BOT_TOKEN, BACKEND_URL
- [ ] Интеграция с backend:
  - При создании партии backend отправляет HTTP-запрос к telegram-bot (или telegram-bot сам polling'ит)
  - Выбран вариант: telegram-bot сам polling'ит backend по REST
- [ ] Проверить: `docker compose up` → бот отвечает на команды
- [ ] Обновить Memory Bank

### M10: Тестирование и CI
**Коммит:** `ci: add GitHub Actions with ruff lint and pytest`

- [ ] Обновить `CHANGES.md`, `PROMPTS.md`, `REPORT.md` — зафиксировать изменения, промпты и историю работы по M10

- [ ] Дописать тесты до минимум 10:
  - unit-тесты: сервисы (изолированные, с mock БД)
  - integration-тесты: API эндпоинты (через TestClient)
  - Тесты: auth, CRUD игроков, CRUD турниров, CRUD партий, рейтинг, статистика, избранное, CSV экспорт, CSV импорт, SSE
- [ ] Настроить `ruff` в `backend/pyproject.toml`:
  - line-length = 100
  - target-version = py312
- [ ] Настроить `ruff` в `telegram-bot/pyproject.toml`
- [ ] Добавить pre-commit hook:
  - Создать `.pre-commit-config.yaml` или git hook `.git/hooks/pre-commit` или через `pyproject.toml` с `ruff check`
  - Вариант: `pre-commit install` + `.pre-commit-config.yaml`
- [ ] Создать `.github/workflows/ci.yml`:
  ```yaml
  name: CI
  on: [push, pull_request]
  jobs:
    lint:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: astral-sh/ruff-action@v1
          with:
            src: backend telegram-bot
    test:
      runs-on: ubuntu-latest
      services:
        postgres:
          image: postgres:16
          env:
            POSTGRES_USER: ct_user
            POSTGRES_PASSWORD: ct_password
            POSTGRES_DB: ct_test
          options: >-
            --health-cmd pg_isready
            --health-interval 10s
            --health-timeout 5s
            --health-retries 5
      steps:
        - uses: actions/checkout@v4
        - name: Install uv
          uses: astral-sh/setup-uv@v3
        - name: Run tests
          run: |
            cd backend
            uv sync
            uv run pytest
          env:
            DATABASE_URL: postgresql+asyncpg://ct_user:ct_password@localhost/ct_test
  ```
- [ ] Проверить CI локально (запуск ruff, pytest)
- [ ] Обновить Memory Bank

### M11: Финальная документация
**Коммит:** `docs: add README and finalize documentation`

- [ ] Создать `README.md`:
  - Описание проекта
  - Стек технологий
  - Предварительные требования (Docker, Docker Compose)
  - Быстрый старт: `docker compose up`
  - Переменные окружения (ссылка на .env.example)
  - Пользователи: admin/admin123, user/user123
  - API документация: `/docs`
  - Команды для разработки
- [ ] Финально проверить и дополнить `ARCHITECTURE.md`:
  - Соответствие реализованной архитектуре
  - Обновить ERD, если были изменения
- [ ] Проверить и дополнить `REPORT.md`:
  - Все ключевые события зафиксированы за все майлстоуны
  - Проблемы и решения описаны
  - Примеры промптов добавлены при необходимости
  - История работы охватывает весь проект
  - Раздел «Удачные и неудачные шаги» покрывает весь проект
- [ ] Проверить `PROMPTS.md`:
  - Все промпты записаны с датами на всём протяжении проекта
- [ ] Проверить `CHANGES.md`:
  - Все изменения записаны хронологически на всём протяжении проекта
- [ ] Финальный коммит и пуш
