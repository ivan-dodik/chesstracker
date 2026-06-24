# Project Brief: Chess Tracker

## Цель проекта
Full-stack приложение для отслеживания шахматных турниров, игроков и их рейтингов. Сервис помогает шахматным болельщикам следить за выступлениями любимых игроков на офлайн-турнирах, отслеживать изменения рейтингов и получать уведомления о результатах партий.

## Ключевые требования

### Функциональные
- CRUD для игроков, турниров, партий с валидацией
- Поиск и фильтрация (турниры по дате/статусу, игроки по имени/рейтингу)
- Дашборд с визуализацией (ApexCharts): график рейтинга, круговая диаграмма результатов, топ-10, избранные
- Пагинация списков
- Адаптивная вёрстка (desktop + mobile)
- Турнирная таблица в реальном времени
- Профиль игрока с историей рейтинга, статистикой
- Рейтинговая история (срезы на дату)
- Head-to-head статистика
- Избранные игроки
- SSE (Server-Sent Events) для real-time уведомлений
- Экспорт турнирной таблицы в CSV
- Импорт результатов турнира из CSV
- Регистрация/авторизация (JWT): admin + user
- Лог активности (UI + запись всех изменений)
- Telegram-bot для уведомлений

### Нефункциональные
- REST API с OpenAPI/Swagger
- 278 тестов (202 unit/integration + 76 E2E)
- CI pipeline (GitHub Actions): ruff lint + pytest
- Docker Compose: одна команда для запуска всех сервисов
- Документация: README.md, ARCHITECTURE.md, REPORT.md

## Стек технологий
- **Backend**: Python 3.12+, FastAPI
- **Database**: PostgreSQL 16, SQLAlchemy + Alembic
- **Frontend**: Jinja2 + HTMX + Alpine.js + ApexCharts
- **Bot**: python-telegram-bot (long-polling)
- **Deployment**: Docker Compose
- **Linter**: ruff
- **CI**: GitHub Actions

## Seed-данные
- 5 турниров (3 завершённых, 2 активных)
- 30+ игроков
- 200+ партий
- 50+ записей истории рейтингов
- 2 пользователя (admin + user)

## Структура модулей (для агента)

Подробное описание каждого модуля — в `memory-bank/`:

| Директория | Описание |
|------------|----------|
| `backend/` | Backend-модули: core, models, schemas, services, API, web, alembic, seed, main, docker |
| `frontend/` | Frontend: шаблоны, CSS, JS (main.js, sse.js) |
| `testing/` | Тесты: API, сервисные, fixtures |
| `telegram-bot/` | Telegram-бот: архитектура и обработчики |
| `infrastructure/` | Docker, CI/CD, pre-commit |
| `config/` | Конфигурация: pyproject.toml, .env |