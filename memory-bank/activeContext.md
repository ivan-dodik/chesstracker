# Active Context: Chess Tracker

## Текущее состояние проекта
Завершён **M1: Архитектура и планирование**. Создана полная документация:
- `project_task.md` — полное техническое задание
- `IMPLEMENTATION_PLAN.md` — детальный план реализации (11 майлстоунов, ~80 шагов)
- `ARCHITECTURE.md` — архитектура, ERD, API endpoints, стек технологий
- `.clinerules/` — правила: report.md, update_prompts.md, git_commit.md, implementation_plan.md, memory-bank.md
- `Memory Bank` — инициализирован, все 6 core-файлов актуальны

Код приложения отсутствует. CHANGES.md и PROMPTS.md содержат полную историю.

## Последние изменения
- Создан `ARCHITECTURE.md` — описание архитектуры, ERD, структура директорий, API endpoints, стек технологий
- Обновлён Memory Bank (activeContext.md, progress.md) — M1 завершён
- Выполнен коммит M1: `docs: add architecture documentation and implementation plan`

## Следующие шаги (приоритетный порядок)
1. ✅ **M1: Архитектура и планирование** — выполнено
2. **M2: Окружение и Docker** — docker-compose.yml, Dockerfile, pyproject.toml, структура директорий
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

## Изученные паттерны и предпочтения
- Управление зависимостями через `uv` (не pip/poetry)
- Линтер `ruff` (flake8 + isort + pyupgrade в одном)
- Все промпты и изменения документируются в PROMPTS.md и CHANGES.md
- Проект должен запускаться одной командой `docker compose up`
- После каждого майлстоуна — коммит + пуш + обновление Memory Bank
- Telegram-bot: long-polling (проще для локальной разработки)
- JWT: localStorage + Bearer Authorization header
- Pre-commit hook: ruff для автоматического форматирования
