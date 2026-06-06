# Progress: Chess Tracker

## Текущий статус
**M2: Окружение и Docker** завершён. Инфраструктура контейнеризации создана, сборка проходит успешно.

## Что работает
- ✅ **M1: Архитектура и планирование** — полная документация, Memory Bank, правила агента
- ✅ **M2: Окружение и Docker**
  - ✅ `backend/pyproject.toml` — все зависимости через uv (fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, alembic, pydantic-settings, python-jose, passlib, python-multipart, httpx, jinja2, aiofiles, sse-starlette)
  - ✅ Dev-зависимости: pytest, pytest-asyncio, ruff
  - ✅ Настроен ruff: line-length=100, target-version=py312
  - ✅ `backend/Dockerfile` — python:3.12-slim + uv
  - ✅ `telegram-bot/pyproject.toml` — зависимости (python-telegram-bot, httpx, pydantic-settings) + ruff
  - ✅ `telegram-bot/Dockerfile` — python:3.12-slim + uv
  - ✅ `.env.example` — шаблон переменных окружения
  - ✅ `docker-compose.yml` — 3 сервиса (db: postgres:16, backend, telegram-bot)
  - ✅ `docker-compose.override.yml` — hot-reload, порт 5432 для db
  - ✅ Структура директорий backend: __init__.py во всех пакетах
  - ✅ Заглушки: `backend/app/main.py` (FastAPI с /health), `telegram-bot/bot.py`
  - ✅ `docker compose build` — успешен

## Что осталось сделать (в порядке приоритета)

### M3: Backend — модели и миграции
- ⬜ `backend/app/core/config.py` — конфигурация (pydantic-settings)
- ⬜ `backend/app/core/database.py` — async engine, sessionmaker, get_db
- ⬜ `backend/app/core/security.py` — hash_password, create_access_token, decode
- ⬜ SQLAlchemy модели: User, Player, Tournament, Game, RatingHistory, Favorite, ActivityLog
- ⬜ Alembic: инициализация, первая миграция
- ⬜ Seed-данные: скрипт наполнения БД
- ⬜ Pydantic схемы: UserCreate, PlayerRead, TournamentCreate, GameCreate и т.д.

### M4: Backend — API: аутентификация и базовые CRUD
- ⬜ Auth: регистрация, логин, JWT
- ⬜ Players: CRUD + поиск/фильтрация
- ⬜ Tournaments: CRUD + поиск/фильтрация + турнирная таблица
- ⬜ Games: CRUD по турам + автоматический подсчёт очков
- ⬜ Тесты (3–4)

### M5: Backend — API: специфичные фичи
- ⬜ Ratings: история рейтинга
- ⬜ Favorites: избранные игроки
- ⬜ Stats: head-to-head, топ-10, общая статистика
- ⬜ Export/Import: CSV
- ⬜ SSE: real-time уведомления
- ⬜ Activity Log: логирование изменений
- ⬜ Тесты (3–4)

### M6: Frontend — базовая структура и навигация
- ⬜ Базовый шаблон (base.html) с навигацией
- ⬜ CSS (адаптивная вёрстка)
- ⬜ JS (Alpine.js, HTMX)
- ⬜ Страницы списков: игроки, турниры
- ⬜ Страница логина
- ⬜ Web-роуты
- ⬜ HTMX-фрагменты (пагинация, строки таблиц)

### M7: Frontend — дашборд и детальные страницы
- ⬜ Дашборд с Chart.js (график рейтинга, круговая диаграмма, топ-10, избранные)
- ⬜ Профиль игрока (история рейтинга, статистика, head-to-head)
- ⬜ Страница турнира (турнирная таблица, партии по турам, CSV)
- ⬜ Alpine.js компоненты (фильтры, формы, модалки)

### M8: Frontend — фичи
- ⬜ Избранные: UI (кнопка, список)
- ⬜ SSE-клиент (EventSource, toast-уведомления)
- ⬜ Экспорт/импорт CSV: UI
- ⬜ Аутентификация на фронте (JWT в localStorage, защита роутов)

### M9: Telegram-bot
- ⬜ `telegram-bot/bot.py` — точка входа, long-polling
- ⬜ Обработчики команд (/start, /subscribe, /unsubscribe)
- ⬜ HTTP-клиент к backend
- ⬜ Уведомления о результатах партий

### M10: Тестирование и CI
- ⬜ Дописать тесты до минимум 10
- ⬜ Настроить ruff в pyproject.toml
- ⬜ Pre-commit hook (ruff)
- ⬜ GitHub Actions: ruff lint + pytest

### M11: Финальная документация
- ⬜ `README.md` — инструкция по запуску
- ⬜ Финальная проверка ARCHITECTURE.md
- ⬜ Финальная проверка REPORT.md, PROMPTS.md, CHANGES.md

## Известные проблемы
- На данный момент нет известных проблем

## Эволюция проектных решений
- **2026-06-06**: Инициализация репозитория, создание ТЗ, Memory Bank
- **2026-06-06 13:35**: Создан IMPLEMENTATION_PLAN.md (11 майлстоунов) и .clinerules/implementation_plan.md
- **2026-06-06 13:35**: Приняты решения: Telegram-bot — long-polling, JWT — localStorage, pre-commit hook — ruff
- **2026-06-06 14:17**: M2 завершён — создана Docker-инфраструктура