# Project Brief: Chess Tracker

## Цель проекта
Full-stack приложение для отслеживания шахматных турниров, игроков и их рейтингов. Сервис помогает шахматным болельщикам следить за выступлениями любимых игроков на офлайн-турнирах, отслеживать изменения рейтингов и получать уведомления о результатах партий.

## Ключевые требования

### Функциональные
- CRUD для игроков, турниров, партий с валидацией
- Поиск и фильтрация (турниры по дате/статусу, игроки по имени/рейтингу)
- Дашборд с визуализацией (Chart.js): график рейтинга, круговая диаграмма результатов, топ-10, избранные
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
- Лог активности
- Telegram-bot для уведомлений

### Нефункциональные
- REST API с OpenAPI/Swagger
- Не менее 10 unit/integration тестов
- CI pipeline (GitHub Actions): ruff lint + pytest
- Docker Compose: одна команда для запуска всех сервисов
- Документация: README.md, ARCHITECTURE.md, REPORT.md

## Стек технологий
- **Backend**: Python 3.12+, FastAPI
- **Database**: PostgreSQL 16, SQLAlchemy + Alembic
- **Frontend**: Jinja2 + HTMX + Alpine.js
- **Bot**: python-telegram-bot
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

Подробное описание каждого модуля — в `memory-bank/modules/`:

| Файл | Описание |
|------|----------|
| `modules/overview.md` | Карта модулей, dependency graph, quick lookup index |
| `modules/core-layer.md` | Config, database, security (JWT, bcrypt) |
| `modules/models-layer.md` | 7 SQLAlchemy ORM моделей |
| `modules/schemas-layer.md` | 7 Pydantic схем валидации |
| `modules/services-layer.md` | 10 сервисов бизнес-логики |
| `modules/api-layer.md` | 12 route-модулей, endpoints, deps |
| `modules/web-layer.md` | Jinja2 шаблоны, CSS, JS (HTMX, Alpine.js) |
| `modules/alembic.md` | Миграции БД |
| `modules/testing.md` | Тесты (pytest, 20 тестов) |
| `modules/telegram-bot.md` | Telegram-бот (stub, M9) |
| `modules/docker-infra.md` | Docker Compose, network, commands |