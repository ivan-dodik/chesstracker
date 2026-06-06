# Active Context: Chess Tracker

## Текущее состояние проекта
Завершён **M2: Окружение и Docker**. Создана вся инфраструктура для контейнеризации и управления зависимостями.

## Последние изменения
- Создан `backend/pyproject.toml` — все зависимости (fastapi, uvicorn, sqlalchemy, asyncpg, alembic, pydantic-settings, python-jose, passlib, python-multipart, httpx, jinja2, aiofiles, sse-starlette) + dev (pytest, pytest-asyncio, ruff)
- Настроен ruff: line-length=100, target-version=py312
- Создан `backend/Dockerfile` — python:3.12-slim, uv, multi-stage copy
- Создан `telegram-bot/pyproject.toml` — зависимости (python-telegram-bot, httpx, pydantic-settings) + dev (ruff)
- Создан `telegram-bot/Dockerfile` — python:3.12-slim, uv
- Создан `.env.example` — шаблон переменных окружения
- Создан `docker-compose.yml` — 3 сервиса (db: postgres:16, backend, telegram-bot)
- Создан `docker-compose.override.yml` — hot-reload для backend, порт 5432 для db
- Создана структура директорий backend (__init__.py во всех пакетах)
- Созданы заглушки: `backend/app/main.py` (FastAPI с /health), `telegram-bot/bot.py`
- Проверена сборка: `docker compose build` успешен (backend + telegram-bot образы построены)

## Следующие шаги (приоритетный порядок)
1. ✅ **M1: Архитектура и планирование** — выполнено
2. ✅ **M2: Окружение и Docker** — выполнено
3. **M3: Backend — модели и БД** — SQLAlchemy модели, Alembic, seed-данные
4. **M4: Backend — API: аутентификация и базовые CRUD**
5. **M5: Backend — API: специфичные фичи** (рейтинг, статистика, SSE, CSV, лог)
6. **M6: Frontend — базовая структура и навигация** (Jinja2, HTMX)
7. **M7: Frontend — дашборд и детальные страницы** (Chart.js, Alpine.js)
8. **M8: Frontend — фичи** (избранное, SSE, CSV, аутентификация)
9. **M9: Telegram-bot** (long-polling)
10. **M10: Тестирование и CI** (GitHub Actions, ruff, pytest)
11. **M11: Финальная документация** (README.md, REPORT.md)

## Активные решения и considerations
- **Структура проекта**: монорепозиторий с backend, frontend (шаблоны внутри backend), telegram-bot как отдельный сервис
- **Фронтенд**: без отдельного сервера — шаблоны Jinja2 отдаются FastAPI, HTMX делает запросы к тем же эндпоинтам
- **Docker**: три контейнера — backend (FastAPI + шаблоны), db (PostgreSQL), telegram-bot
- **Telegram-bot**: отдельный микросервис в том же compose-файле, long-polling (не webhook)
- **Аутентификация**: JWT токены в localStorage, два предзаполненных аккаунта (admin, user)
- **Pre-commit hook**: ruff (будет настроен в M10)
- **Dockerfile**: alembic/ и alembic.ini не копируются на этапе M2 (будут созданы в M3)
- **docker-compose.override.yml**: для разработки монтирует ./backend/app:/app/app для hot-reload

## Изученные паттерны и предпочтения
- Управление зависимостями через `uv` (не pip/poetry)
- Линтер `ruff` (flake8 + isort + pyupgrade в одном)
- Все промпты и изменения документируются в PROMPTS.md и CHANGES.md
- Проект должен запускаться одной командой `docker compose up`
- После каждого майлстоуна — коммит + пуш + обновление Memory Bank
- Telegram-bot: long-polling (проще для локальной разработки)
- JWT: localStorage + Bearer Authorization header
- Pre-commit hook: ruff для автоматического форматирования