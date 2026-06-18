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

- [x] Создать `ARCHITECTURE.md`:
  - Описание архитектуры (текст + диаграмма из systemPatterns.md)
  - ERD (из systemPatterns.md)
  - План разработки (ссылка на IMPLEMENTATION_PLAN.md)
  - Стек технологий
  - Структура директорий
- [x] Убедиться, что `IMPLEMENTATION_PLAN.md` (этот файл) содержит все актуальные чекмаки
- [x] Создать `REPORT.md` — начальная структура отчёта (AI-инструменты, примеры промптов, ключевые проблемы и решения, удачные/неудачные шаги, история работы за M1)
- [x] Обновить Memory Bank (activeContext.md, progress.md)

### M2: Окружение и Docker
**Коммит:** `chore: setup docker environment and project scaffolding`

- [x] Создать `backend/pyproject.toml` через `uv init`:
  - Зависимости: fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, alembic, pydantic-settings, python-jose[cryptography], passlib[bcrypt], python-multipart, httpx, jinja2, aiofiles, sse-starlette
  - Dev-зависимости: pytest, pytest-asyncio, httpx, ruff
  - Конфигурация ruff
- [x] Создать `backend/Dockerfile`:
  - FROM python:3.12-slim
  - Установка uv
  - Копирование pyproject.toml, uv.lock
  - `uv sync`
  - Копирование кода
  - CMD: uvicorn app.main:app --host 0.0.0.0 --port 8000
- [x] Создать `telegram-bot/pyproject.toml`:
  - Зависимости: python-telegram-bot, httpx, pydantic-settings
  - Dev-зависимости: ruff
- [x] Создать `telegram-bot/Dockerfile`:
  - FROM python:3.12-slim
  - Аналогично backend, CMD: python bot.py
- [x] Создать `.env.example`:
  - DATABASE_URL, SECRET_KEY, TG_BOT_TOKEN, и т.д.
- [x] Создать `docker-compose.yml`:
  - **db**: postgres:16, volume, env, healthcheck
  - **backend**: build: ./backend, depends_on: db, ports: 8000:8000, env_file
  - **telegram-bot**: build: ./telegram-bot, depends_on: backend, env_file
- [x] Создать `docker-compose.override.yml` для разработки:
  - backend: volumes для hot-reload, ports
  - db: ports 5432:5432
- [x] Создать `postgres-init/init.sql` — создание БД и пользователя (optional, можно через POSTGRES_* env)
- [x] Создать структуру директорий backend:
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
- [x] Проверить: `docker compose build` успешен
- [x] Обновить `CHANGES.md`, `PROMPTS.md`, `REPORT.md` — зафиксировать изменения, промпты и историю работы по M2
- [x] Обновить Memory Bank

### M3: Backend — модели и база данных
**Коммит:** `feat: add SQLAlchemy models and initial migration`

- [x] Создать `backend/app/core/config.py`:
  - Pydantic BaseSettings: DATABASE_URL, SECRET_KEY, TG_BOT_TOKEN, DEBUG, и т.д.
- [x] Создать `backend/app/core/database.py`:
  - async engine, async sessionmaker, async get_db dependency
- [x] Создать `backend/app/core/security.py`:
  - hash_password(), verify_password() — passlib bcrypt
  - create_access_token(), decode_access_token() — python-jose JWT
- [x] Создать модели SQLAlchemy в `backend/app/models/`:
  - **User**: id, username, hashed_password, role (admin/user), created_at
  - **Player**: id, name, rating, city, avatar_url, created_at, updated_at
  - **Tournament**: id, name, start_date, end_date, location, rounds, type (classic/blitz/rapid), status (active/completed), created_at, updated_at
  - **Game**: id, tournament_id (FK), round, white_player_id (FK), black_player_id (FK), result (1-0/0-1/½-½), played_at, created_at
  - **RatingHistory**: id, player_id (FK), rating, date, tournament_id (FK nullable)
  - **Favorite**: id, user_id (FK), player_id (FK), created_at (unique constraint user+player)
  - **ActivityLog**: id, user_id (FK), action, entity_type, entity_id, old_values (JSON), new_values (JSON), timestamp
- [x] Создать `backend/app/models/__init__.py` — re-export всех моделей, Base
- [x] Инициализировать Alembic: `alembic init alembic` внутри backend/
- [x] Настроить `alembic/env.py` — подключение к DATABASE_URL, import моделей
- [x] Создать первую миграцию: `alembic revision --autogenerate -m "initial"`
- [x] Накатить миграцию: `alembic upgrade head`
- [x] Создать `backend/app/seed.py`:
  - 2 пользователя (admin/admin123, user/user123)
  - 5 турниров (3 completed, 2 active)
  - 30+ игроков с рейтингами
  - 200+ партий
  - 50+ записей RatingHistory
  - Несколько Favorite записей
- [x] Создать Pydantic схемы в `backend/app/schemas/`:
  - UserCreate, UserRead, Token
  - PlayerCreate, PlayerRead, PlayerList
  - TournamentCreate, TournamentRead, TournamentList, TournamentStandings
  - GameCreate, GameRead, GameResult
  - RatingHistoryRead
  - FavoriteRead
  - ActivityLogRead
- [x] Проверить seed: запустить скрипт через `docker compose run --rm backend python -m app.seed`
- [x] Обновить `CHANGES.md`, `PROMPTS.md`, `REPORT.md` — зафиксировать изменения, промпты и историю работы по M3
- [x] Обновить Memory Bank

### M4: Backend — API: аутентификация и базовые CRUD
**Коммит:** `feat: implement auth and basic CRUD API`

- [x] Создать `backend/app/api/deps.py`:
  - `get_db` — async session
  - `get_current_user` — JWT из Authorization header
  - `get_current_admin` — проверка роли admin
- [x] Создать `backend/app/api/auth.py`:
  - `POST /api/auth/login` — username + password → JWT
  - `POST /api/auth/register` — создание нового пользователя (admin only)
  - `GET /api/auth/me` — текущий пользователь
- [x] Создать `backend/app/services/player_service.py` + `backend/app/api/players.py`:
  - `GET /api/players` — список с пагинацией (page, per_page), поиском (name, rating, city)
  - `POST /api/players` — создание (admin only)
  - `GET /api/players/{id}` — детальная информация
  - `PUT /api/players/{id}` — обновление (admin only)
  - `DELETE /api/players/{id}` — удаление (admin only)
- [x] Создать `backend/app/services/tournament_service.py` + `backend/app/api/tournaments.py`:
  - `GET /api/tournaments` — список с пагинацией, фильтрацией (date, location, status)
  - `POST /api/tournaments` — создание (admin only)
  - `GET /api/tournaments/{id}` — детальная информация
  - `PUT /api/tournaments/{id}` — обновление (admin only)
  - `DELETE /api/tournaments/{id}` — удаление (admin only)
- [x] Создать `backend/app/services/game_service.py` + `backend/app/api/games.py`:
  - `GET /api/tournaments/{id}/games` — список партий турнира (с пагинацией по турам)
  - `POST /api/tournaments/{id}/games` — добавление партии (admin only)
  - `PUT /api/games/{id}` — обновление результата (admin only)
  - `DELETE /api/games/{id}` — удаление (admin only)
  - Автоматический подсчёт очков для турнирной таблицы
  - `GET /api/tournaments/{id}/standings` — турнирная таблица (сортировка по очкам)
- [x] Создать `backend/app/api/router.py` — объединение всех роутеров в api_router
- [x] Создать `backend/app/main.py`:
  - FastAPI app с lifespan (создание таблиц через alembic upgrade или проверка)
  - Подключение api_router
  - Монтирование static files
  - Настройка Jinja2Templates
  - CORS middleware
  - Swagger UI по /docs
- [x] Написать тесты (3–4): `backend/tests/test_auth.py`, `backend/tests/test_players.py`
- [x] Проверить Swagger UI: открыть /docs, протестировать эндпоинты
- [x] Обновить `CHANGES.md`, `PROMPTS.md`, `REPORT.md` — зафиксировать изменения, промпты и историю работы по M4
- [x] Обновить Memory Bank

### M5: Backend — API: специфичные фичи
**Коммит:** `feat: add ratings, stats, favorites, SSE, CSV, activity log`

- [x] Создать `backend/app/services/rating_service.py` + `backend/app/api/ratings.py`:
  - `GET /api/players/{id}/rating-history` — история рейтинга с фильтром по дате
- [x] Создать `backend/app/services/favorite_service.py` + `backend/app/api/favorites.py`:
  - `GET /api/favorites` — избранные текущего пользователя
  - `POST /api/favorites/{player_id}` — добавить в избранное
  - `DELETE /api/favorites/{player_id}` — удалить из избранного
- [x] Создать `backend/app/services/stats_service.py` + `backend/app/api/stats.py`:
  - `GET /api/stats/head-to-head/{player1_id}/{player2_id}` — личные встречи
  - `GET /api/stats/top-rated` — топ-10 по рейтингу
  - `GET /api/stats/overall/{player_id}` — общая статистика (победы/ничьи/поражения)
- [x] Создать `backend/app/services/sse_service.py` + `backend/app/api/sse.py`:
  - `GET /api/events` — SSE endpoint (подписка на события)
  - Отправка событий при: создании партии, изменении результата, изменении рейтинга
- [x] Создать `backend/app/services/export_service.py` + `backend/app/api/export.py`:
  - `GET /api/tournaments/{id}/export/csv` — экспорт турнирной таблицы в CSV
- [x] Создать `backend/app/services/import_service.py` + `backend/app/api/import_route.py`:
  - `POST /api/tournaments/{id}/import/csv` — импорт результатов из CSV (маппинг колонок: игрок, тур, соперник, результат)
- [x] Создать `backend/app/services/activity_log_service.py` + `backend/app/api/activity_log.py`:
  - `GET /api/activity-log` — лог активности с пагинацией
  - Интегрировать логирование во все CRUD-операции (создание/редактирование/удаление)
- [x] Написать тесты (3–4): `backend/tests/test_ratings.py`, `backend/tests/test_stats.py`, `backend/tests/test_favorites.py`
- [x] Обновить `CHANGES.md`, `PROMPTS.md`, `REPORT.md` — зафиксировать изменения, промпты и историю работы по M5
- [x] Обновить Memory Bank

### M6: Frontend — базовая структура и навигация
**Коммит:** `feat: add base frontend with Jinja2 templates and HTMX`

- [x] Создать `backend/app/static/css/style.css`:
  - Адаптивная вёрстка (desktop + mobile)
  - CSS custom properties для темизации
  - Стили для навигации, таблиц, форм, карточек
- [x] Создать `backend/app/static/js/main.js`:
  - Базовые Alpine.js компоненты
  - HTMX инициализация
- [x] Создать `backend/app/templates/base.html`:
  - DOCTYPE html, head (meta viewport, title, CSS, JS)
  - Навигация (логотип, ссылки: дашборд, игроки, турниры; логин/логаут)
  - Блок для flash-сообщений
  - Блок content
  - Footer
  - Подключение: htmx.org, alpine.js, chart.js (CDN или локально)
- [x] Создать `backend/app/templates/login.html`:
  - Форма логина (username, password)
  - HTMX: отправка формы → получение JWT → сохранение в localStorage
- [x] Создать web-роуты в `backend/app/api/web.py`:
  - `GET /` — дашборд (index.html)
  - `GET /players` — список игроков (players/list.html)
  - `GET /tournaments` — список турниров (tournaments/list.html)
  - `GET /login` — страница входа
  - (детальные страницы — в M7)
- [x] Создать `backend/app/templates/index.html` (каркас дашборда):
  - Разделы: топ-10 игроков, последние результаты, избранные (заглушки)
- [x] Создать `backend/app/templates/players/list.html`:
  - Таблица игроков с HTMX-пагинацией
  - Поле поиска по имени (hx-trigger: keyup changed delay:500ms)
- [x] Создать `backend/app/templates/tournaments/list.html`:
  - Таблица турниров с HTMX-пагинацией
  - Фильтры: статус, дата
- [x] Создать HTMX-фрагменты: `backend/app/templates/partials/`:
  - `player_row.html` — строка таблицы игрока
  - `tournament_row.html` — строка таблицы турнира
  - `pagination.html` — компонент пагинации
- [x] Проверить, что все страницы открываются (дашборд, списки, логин)
- [x] Обновить `CHANGES.md`, `PROMPTS.md`, `REPORT.md` — зафиксировать изменения, промпты и историю работы по M6
- [x] Обновить Memory Bank

### M7: Frontend — дашборд и детальные страницы
**Коммит:** `feat: add dashboard with Chart.js and detail pages`

- [x] Реализовать дашборд (`templates/index.html`):
  - График рейтинга топ-игрока (Chart.js, line chart) — `GET /api/players/{id}/rating-history`
  - Круговая диаграмма результатов (Chart.js, doughnut) — `GET /api/stats/overall/{id}`
  - Топ-10 игроков (список) — `GET /api/stats/top-rated`
  - Избранные игроки (список с последними результатами)
- [x] Создать `backend/app/templates/players/detail.html`:
  - Профиль игрока: имя, рейтинг, город, аватар
  - График истории рейтинга (Chart.js)
  - Список сыгранных турниров с результатами
  - Общая статистика (победы/ничьи/поражения)
  - Head-to-head с другим игроком (выпадающий список)
- [x] Создать `backend/app/templates/tournaments/detail.html`:
  - Информация о турнире: название, даты, место, тип, статус
  - Турнирная таблица (таблица с очками, сортировка)
  - Партии по турам (аккордеон/табы)
  - Кнопка экспорта CSV
  - Форма импорта CSV (для админа)
- [x] Создать Alpine.js компоненты:
  - Фильтры для списков (x-data, x-model)
  - Формы создания/редактирования (x-show для модалок)
  - Head-to-head селектор
- [x] Создать дополнительный CSS для компонентов дашборда
- [x] Проверить адаптивную вёрстку на мобильном разрешении (Chrome DevTools)
- [x] Обновить `CHANGES.md`, `PROMPTS.md`, `REPORT.md` — зафиксировать изменения, промпты и историю работы по M7
- [x] Обновить Memory Bank

### M8: Frontend — фичи (избранное, SSE, CSV, аутентификация)
**Коммит:** `feat: add favorites UI, SSE client, CSV import/export, auth UI`

- [x] Реализовать избранное на фронте:
  - Кнопка "★" на профиле игрока (Alpine.js, hx-post/hx-delete)
  - Список избранных на дашборде
- [x] Реализовать SSE-клиент:
  - `backend/app/static/js/sse.js` — EventSource подключение к `/api/events`
  - Toast-уведомления при новых событиях
- [x] Реализовать экспорт CSV:
  - Кнопка "Экспорт CSV" на странице турнира → `GET /api/tournaments/{id}/export/csv` → скачивание
- [x] Реализовать импорт CSV:
  - Форма загрузки файла на странице турнира (для админа)
  - HTMX: hx-encoding="multipart/form-data"
- [x] Реализовать аутентификацию на фронте:
  - Форма логина → POST /api/auth/login → сохранение JWT в localStorage
  - HTMX: добавление Authorization header через hx-headers или Alpine.js
  - Защита роутов: перенаправление на /login если нет токена
  - Индикация: показать username в навигации, кнопка logout
- [x] Проверить полный user flow:
  - Неавторизованный: просмотр дашборда, списков, профилей
  - Авторизованный (user): избранное, уведомления
  - Админ: создание/редактирование турниров, партий, импорт CSV
- [x] Обновить `CHANGES.md`, `PROMPTS.md`, `REPORT.md` — зафиксировать изменения, промпты и историю работы по M8
- [x] Обновить Memory Bank

### M9: Telegram-bot
**Коммит:** `feat: add Telegram bot for notifications`

- [x] Создать `telegram-bot/bot.py`:
  - Инициализация Application (python-telegram-bot)
  - Регистрация обработчиков команд
  - Запуск long-polling: `application.run_polling()`
- [x] Создать `telegram-bot/handlers/start.py`:
  - `/start` — приветственное сообщение, инструкция
- [x] Создать `telegram-bot/handlers/subscribe.py`:
  - `/subscribe` — подписка на уведомления (сохраняет chat_id)
  - `/unsubscribe` — отписка
- [x] Создать `telegram-bot/services/api_client.py`:
  - HTTP-клиент (httpx.AsyncClient) для запросов к backend
  - GET /api/tournaments/active — получить активные турниры
  - GET /api/tournaments/{id}/games/latest — получить последние результаты
- [x] Создать `telegram-bot/services/notifier.py`:
  - Периодическая проверка новых результатов (каждые N секунд)
  - Отправка уведомлений подписанным пользователям
- [x] Настроить конфигурацию: `telegram-bot/config.py` (pydantic-settings):
  - TG_BOT_TOKEN, BACKEND_URL
- [x] Интеграция с backend:
  - При создании партии backend отправляет HTTP-запрос к telegram-bot (или telegram-bot сам polling'ит)
  - Выбран вариант: telegram-bot сам polling'ит backend по REST
- [x] Проверить: `docker compose up` → бот отвечает на команды
- [x] Обновить `CHANGES.md`, `PROMPTS.md`, `REPORT.md` — зафиксировать изменения, промпты и историю работы по M9
- [x] Обновить Memory Bank

### M10: Тестирование и CI
**Коммит:** `ci: add GitHub Actions with ruff lint and pytest`

- [x] Дописать тесты до минимум 10:
  - unit-тесты: сервисы (изолированные, с mock БД)
  - integration-тесты: API эндпоинты (через TestClient)
  - Тесты: auth, CRUD игроков, CRUD турниров, CRUD партий, рейтинг, статистика, избранное, CSV экспорт, CSV импорт, SSE
- [x] Настроить `ruff` в `backend/pyproject.toml`:
  - line-length = 100
  - target-version = py312
- [x] Настроить `ruff` в `telegram-bot/pyproject.toml`
- [x] Добавить pre-commit hook:
  - Создать `.pre-commit-config.yaml` или git hook `.git/hooks/pre-commit` или через `pyproject.toml` с `ruff check`
  - Вариант: `pre-commit install` + `.pre-commit-config.yaml`
- [x] Создать `.github/workflows/ci.yml`:
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
- [x] Проверить CI локально (запуск ruff, pytest)
- [x] Обновить `CHANGES.md`, `PROMPTS.md`, `REPORT.md` — зафиксировать изменения, промпты и историю работы по M10
- [x] Обновить Memory Bank

### M11: Финальная документация
**Коммит:** `docs: add README and finalize documentation`

- [x] Создать `README.md`:
  - Описание проекта
  - Стек технологий
  - Предварительные требования (Docker, Docker Compose)
  - Быстрый старт: `docker compose up`
  - Переменные окружения (ссылка на .env.example)
  - Пользователи: admin/admin123, user/user123
  - API документация: `/docs`
  - Команды для разработки
- [x] Финально проверить и дополнить `ARCHITECTURE.md`:
  - Соответствие реализованной архитектуре
  - Обновить ERD, если были изменения
- [x] Проверить и дополнить `REPORT.md`:
  - Все ключевые события зафиксированы за все майлстоуны
  - Проблемы и решения описаны
  - Примеры промптов добавлены при необходимости
  - История работы охватывает весь проект
  - Раздел «Удачные и неудачные шаги» покрывает весь проект
- [x] Проверить `PROMPTS.md`:
  - Все промпты записаны с датами на всём протяжении проекта
- [x] Проверить `CHANGES.md`:
  - Все изменения записаны хронологически на всём протяжении проекта
- [x] Финальный коммит и пуш

---

## Пост-релиз: Установка агентских скиллов

После завершения M1–M11 были установлены агентские скиллы для Cline. Этот шаг **не является** частью майлстоунов M1–M11, но должен быть задокументирован при установке новых скиллов в будущем.

**Выполнено 2026-06-06 21:49:**
- Установлены 5 пакетов: mattpocock/skills (29), anthropics/skills (18), obra/superpowers (14), supabase/agent-skills (2), xixu-me/skills (12)
- Создан `skills-lock.json` с хешами всех скиллов
- Обновлён `.gitignore` (добавлен `.agents/`)
- Скиллы доступны через `use_skill`

**Документирование скиллов** (выполнено 2026-06-06 21:57):
- PROMPTS.md — запись о промпте установки скиллов
- REPORT.md — запись в «История работы» + «Ключевые проблемы и решения»
- Memory Bank — techContext.md, activeContext.md, progress.md
- .clinerules/memory-bank.md — правило «Установка агентских скиллов»
- CHANGES.md — запись уже была добавлена при установке
- `skills-lock.json` — закоммичен в репозиторий

---

## M12: TDD-инфраструктура и правила
**Коммит:** `test: add TDD rules, pytest-cov, pre-commit hooks`

- [x] Установить `pytest-cov` в dev-зависимости backend
- [x] Создать `.clinerules/tdd.md`:
  - Red-Green-Refactor (обязателен для нового кода)
  - Таблица соответствия «файл → какие тесты запускать»
  - Критерии завершения задачи: перед attempt_completion → полный прогон pytest + ruff check
  - Pre-commit: ruff check + pytest
- [x] Обновить `.pre-commit-config.yaml` — добавить hook pytest для backend
- [x] Обновить `pyproject.toml` — testpaths, addopts
- [x] Обновить `.github/workflows/ci.yml`:
  - pytest с `--cov` флагом
  - Добавить job `test-telegram-bot`
- [x] Обновить `IMPLEMENTATION_PLAN.md` (этот файл) — добавить M12–M17
- [x] **Документирование и коммит**:
  - CHANGES.md, PROMPTS.md, REPORT.md
  - Memory Bank (activeContext.md, progress.md)
  - `git add -A && git commit -m "test: add TDD infrastructure and test rules" && git push`

## M13: API-тесты — Турниры, Игры, Export, Import
**Коммит:** `test: add API tests for tournaments, games, export, import`

Пишем по TDD: один тест → минимальный код (если не хватает) → зелёный.

- [x] `test_tournaments.py` — 7 тестов (List, Create admin/403, Get, Update, Delete, Standings, empty list)
- [x] `test_games.py` — 6 тестов (List by tournament, Create admin/401, Update result, Delete, nonexistent 404)
- [x] `test_export.py` — 3 теста (Export CSV 200, nonexistent 404, empty tournament)
- [x] `test_import_route.py` — 4 теста (Import success admin, 401 unauth, invalid CSV, missing file)
- [x] `test_players.py` — +2 теста (Update player admin, Delete player admin)
- [x] `test_auth.py` — +2 теста (Register by admin 201, Register by non-admin 403)
- [x] **Документирование и коммит**

## M14: API-тесты — Activity Log, Health, краевые случаи
**Коммит:** `test: add tests for activity log, health, auth edge cases`

- [x] `test_activity_log.py` — 4 теста (Get log admin OK, user=403, unauth=401, pagination)
- [x] `test_health.py` — 2 теста (GET /health → {"status":"ok"}, GET /docs → 200)
- [x] `test_ratings.py` — +2 теста (Nonexistent player 404, empty date range)
- [x] `test_stats.py` — +2 теста (Head-to-head nonexistent 404, player with no games)
- [x] `test_favorites.py` — +2 теста (Add favorite to nonexistent player 404, double delete 404)
- [x] **Документирование и коммит**

## M15: Unit-тесты сервисов
**Коммит:** `test: add unit tests for all service modules`

Создать `backend/tests/services/`. Тестируем бизнес-логику через SQLite (без моков).

- [x] Создать `backend/tests/services/__init__.py`
- [x] `test_player_service.py` — 3 теста (CRUD, search/filter)
- [x] `test_tournament_service.py` — 3 теста (CRUD, standings calculation)
- [x] `test_game_service.py` — 3 теста (CRUD, standings update)
- [x] `test_rating_service.py` — 2 теста (History, date filter)
- [x] `test_stats_service.py` — 3 теста (Top-rated ties, overall, head-to-head)
- [x] `test_favorite_service.py` — 2 теста (Add/remove, duplicate)
- [x] `test_activity_log_service.py` — 2 теста (Create, get paginated)
- [x] `test_export_service.py` — 2 теста (Export CSV, empty tournament)
- [x] **Документирование и коммит**

## M16: Telegram-bot тесты и CI
**Коммит:** `test: add telegram-bot tests and CI job`

- [x] Добавить `pytest`, `pytest-asyncio`, `pytest-httpx` в dev-зависимости telegram-bot
- [x] Создать `telegram-bot/tests/__init__.py`
- [x] Создать `telegram-bot/tests/conftest.py` (mock backend server)
- [x] `test_api_client.py` — 3 теста (get tournaments, get games, error/retry)
- [x] `test_notifier.py` — 3 теста (notify subscribers, skip if no new, error recovery)
- [x] Обновить `.github/workflows/ci.yml` — job `test-telegram-bot`
- [x] Обновить `.pre-commit-config.yaml` — ruff hook для telegram-bot tests
- [x] **Документирование и коммит**

## M17: E2E тесты (Playwright)
**Коммит:** `test: add E2E browser tests with Playwright`

- [x] Установить Playwright: `pip install playwright && playwright install chromium`
- [x] Создать `backend/tests/e2e/`:
  - `test_login.py` — логин admin/admin123, проверка дашборда
  - `test_login_fail.py` — неверный пароль, сообщение об ошибке
  - `test_navigation.py` — навигация по страницам
- [x] Создать `scripts/run_e2e.py` — запуск backend через `with_server.py` + Playwright
- [x] Обновить `.github/workflows/ci.yml` — добавить job `e2e` (с PostgreSQL)

---

## M18: Исправление багов — CSV экспорт + debounce фильтрации
**Коммит:** `fix: CSV export auth and tournament filter debounce`

Замечания преподавателя: ошибка CSV экспорта, слишком много запросов при быстрой печати в поле фильтра турниров.

- [x] **CSV экспорт** — исправить авторизацию:
  - `backend/app/api/export.py`: заменить `get_current_user` → `get_current_user_for_web` (поддержка cookie)
  - Причина: `<a download>` не отправляет Authorization header, endpoint требует Bearer token → 401
  - Альтернатива: изменить frontend на JS fetch с auth header + blob download (надёжнее)
  - Затронутые файлы: `backend/app/api/export.py`, `backend/app/templates/tournaments/detail.html`
- [x] **Debounce фильтрации турниров**:
  - `backend/app/templates/tournaments/list.html`: добавить debounce (300ms) на `onkeyup="loadTournamentsPage(1)"`
  - Реализация: обернуть вызов в `setTimeout` с `clearTimeout` предыдущего таймера
  - Затронутый файл: `backend/app/templates/tournaments/list.html`
- [x] Тесты: проверить CSV экспорт через `test_export.py`, добавить тест на debounce (опционально)
- [x] ruff check
- [x] **Документирование и коммит**

## M19: Расчёт рейтинга + RatingHistory
**Коммит:** `feat: add rating calculation and RatingHistory on game result`

Замечание преподавателя: добавляю партию в турнир, рейтинг не меняется. Рейтинговая история не заполняется.

- [x] Создать `backend/app/services/rating_calculation_service.py`:
  - Функция `calculate_elo_rating(player_rating, opponent_rating, result, k_factor=32)` → новый рейтинг
  - Функция `update_ratings_after_game(db, game)` → обновляет Player.rating + создаёт RatingHistory
  - Функция `recalculate_all_ratings(db, tournament_id)` → пересчёт рейтингов по результатам турнира
  - Формула ELO: `E = 1 / (1 + 10^((Rb - Ra)/400))`, `Ra' = Ra + K * (Sa - Ea)`
  - Результаты: 1-0 → Sa=1 (победа белых), 0-1 → Sa=0, ½-½ → Sa=0.5
- [x] Интегрировать в `backend/app/services/game_service.py`:
  - `create_game()`: если result не None → вызвать `update_ratings_after_game()`
  - `update_game_result()`: если result изменился → пересчитать рейтинги
  - Добавить SSE event `rating_updated` при изменении рейтинга
- [x] Добавить `tournament_id` в RatingHistory при записи (для отслеживания по турнирам)
- [x] Логировать изменения рейтинга в ActivityLog (old_values: {rating: old}, new_values: {rating: new})
- [x] Тесты:
  - `tests/services/test_rating_calculation_service.py` — unit-тесты расчёта ELO (победа белых, победа чёрных, ничья, k-factor)
  - Обновить `tests/services/test_game_service.py` — интеграционные тесты (создание игры обновляет рейтинг)
- [x] ruff check
- [x] **Документирование и коммит**

## M20: SSE real-time — обновление данных на страницах
**Коммит:** `feat: SSE real-time updates for dashboard and tournament pages`

Замечания преподавателя: рейтинг в админке меняю, в топ 10 не обновляется. Уведомления в реальном времени не выполнены.

- [x] **Серверная часть** — `backend/app/services/game_service.py`:
  - Добавить `publish_event("rating_updated", {...})` при изменении рейтинга (после M19)
  - Добавить `publish_event("game_created", {...})` с полными данными (имена игроков, результат)
  - Добавить `publish_event("game_result_updated", {...})` с полными данными
- [x] **Дашборд** — `backend/app/templates/index.html`:
  - Добавить SSE listener на событие `rating_updated` → автоматически обновить top-10 таблицу
  - Реализация: `window.sseClient.eventSource.addEventListener('rating_updated', ...)` → fetch `/api/stats/top-rated` → перерисовать таблицу
- [x] **Страница турнира** — `backend/app/templates/tournaments/detail.html`:
  - Добавить SSE listener на `game_created` и `game_result_updated` → обновить standings + games
  - Реализация: fetch standings + games, перерисовать accordion и таблицу
- [x] **SSE клиент** — `backend/app/static/js/sse.js`:
  - Добавить возможность регистрации callback'ов на события извне (не только toast)
  - Метод `on(eventName, callback)` для подписки страниц
  - Автоматическая отписка при `htmx:afterSwap` (старые listeners)
- [x] Тесты: E2E тест через Playwright (создать партию в другой вкладке → проверить обновление)
- [x] ruff check
- [x] **Документирование и коммит**

## M21: Круговая диаграмма на странице игрока
**Коммит:** `feat: add results distribution doughnut chart on player detail page`

Замечание преподавателя: "круговая диаграмма результатов (победы/ничьи/поражения)" — требование не выполнено на странице игрока.

- [x] Добавить doughnut chart в `backend/app/templates/players/detail.html`:
  - Новый `<div class="card">` с заголовком "🥧 Распределение результатов"
  - `<canvas x-ref="resultsChart">` для Chart.js doughnut
  - Данные: `overallStats.wins`, `overallStats.losses`, `overallStats.draws`
  - Цвета: победы (#27ae60), поражения (#e74c3c), ничьи (#f39c12)
  - Аналогичный компонент уже есть на дашборде (`overallStatsChart` в main.js) — переиспользовать логику
- [x] Добавить метод `renderResultsChart()` в Alpine.js компонент `playerDetail`:
  - Вызывать после загрузки `overallStats` (в `init()`)
  - Уничтожать предыдущий chart перед созданием нового (guard от дублирования canvas)
- [x] Затронутые файлы: `backend/app/templates/players/detail.html`
- [x] Тесты: E2E проверка что canvas рендерится, unit-тест `get_overall_stats()` возвращает корректные данные
- [x] ruff check
- [x] **Документирование и коммит**

## M22: Лог активности — UI-страница + аудит рейтинга
**Коммит:** `feat: activity log web page and rating change audit`

Замечание преподавателя: "Лог активности: фиксация всех изменений с указанием пользователя, времени и значений до/после — нет аудита."

- [x] **UI-страница лога активности** (admin only):
  - `backend/app/api/web.py`: добавить маршрут `GET /activity-log`
  - Создать `backend/app/templates/activity_log.html`:
    - Таблица с колонками: Дата, Пользователь, Действие, Сущность, ID, До, После
    - Фильтры: entity_type (player/tournament/game), action (create/update/delete), дата
    - Пагинация
  - Добавить ссылку "📋 Лог активности" в навигацию (base.html, только для admin)
- [x] **Аудит рейтинга** (после M19):
  - В `rating_calculation_service.py`: логировать каждое изменение рейтинга через `log_activity()`
  - Old values: `{rating: old_rating, player_name: name}`
  - New values: `{rating: new_rating, change: new - old, tournament_id: tid}`
- [x] Тесты:
  - Тест API `/api/activity-log` — проверка что записи создаются
  - Тест что рейтинговые изменения логируются
- [x] ruff check
- [x] **Документирование и коммит**
