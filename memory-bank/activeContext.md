# Active Context: Chess Tracker

## Текущее состояние проекта
Проект полностью реализован. Задокументирована проблема с циклическим редиректом после логина (см. BUGS.md).

## Последние изменения
- Исправлена ошибка `AttributeError: 'NoneType' object has no attribute 'run_repeating'` при запуске telegram-bot
- Добавлен extra `[job-queue]` для `python-telegram-bot`
- Перегенерирован `uv.lock`: добавлены apscheduler v3.11.2, tzdata v2026.2, tzlocal v5.3.1
- Исправлена проблема root-файлов в Docker volumes (user: UID/GID)
- Graceful shutdown бота при фейковом токене (is_token_valid, restart: "no")
- Исправлена ошибка uv cache (Permission denied) — добавлен appuser в Dockerfile
- Исправлены фронтенд-ошибки Alpine.js (порядок загрузки скриптов, defer, alpine:init)
- **Исправлена проблема аутентификации (01:24)**: обработчик `htmx:responseError` теперь проверяет наличие токена, добавлено логирование
- **Создан BUGS.md (02:20)**: полная документация проблемы циклического редиректа после логина с хронологией исправлений, анализом корневой причины и приоритетом дальнейших работ

## Следующие шаги
- Устранить гонку между HTMX `hx-trigger="load"` и Alpine.js `x-show` на дашборде (защищённые эндпоинты отправляют запросы до того, как Alpine скрыл секции для неаутентифицированных пользователей)
- Альтернатива: заменить `hx-trigger="load"` на Alpine-управляемую загрузку для защищённых секций
- Увеличить задержку перед редиректом после логина (100ms → 300ms) или перейти на Promise-based подход

## Активные решения и considerations
- **Тесты**: SQLite (aiosqlite) используется для тестов вместо PostgreSQL, чтобы избежать проблем с event loop'ами. `settings.DATABASE_URL` переопределяется в conftest.py перед импортом app модулей.
- **bcrypt**: зафиксирована версия 4.0.1 из-за несовместимости passlib с bcrypt 5.x
- **Alembic**: настроен на async режим через asyncio.run()
- **Seed-данные**: пересоздают таблицы (drop_all + create_all) при каждом запуске
- **SSE**: реализован in-memory pub/sub через asyncio.Queue, подходит для одного процесса
- **ActivityLog**: JSON-поля (old_values, new_values) хранятся как сериализованные строки в SQLite/PostgreSQL
- **Jinja2**: используется кастомный Environment с cache_size=0 (обход несовместимости Jinja2 3.1.x со Starlette Jinja2Templates)
- **Шаблоны**: не используют Flask-специфичные функции (get_flashed_messages заменён на JS-управление flash-сообщениями)
- **Chart.js**: подключён через CDN (chart.umd.min.js v4.4.7), используется для line chart (история рейтинга) и doughnut chart (общая статистика)
- **Alpine.js**: компоненты ratingChart, overallStatsChart, playerDetail, tournamentDetail, headToHead, accordion
- **GameRead**: расширен полями white_player_name, black_player_name
- **TournamentStandings**: расширен полями wins, draws, losses
- **Агентские скиллы Cline**: установлены 5 пакетов (75+ скиллов). Доступны через `use_skill`. Подробнее: `memory-bank/techContext.md` (раздел «Инструменты разработки»), `.clinerules/memory-bank.md` (раздел «Установка агентских скиллов»).
- **Проблема аутентификации**: Частично исправлена. Корневая причина — гонка между HTMX `hx-trigger="load"` и Alpine.js `x-show`. Создан BUGS.md с полным анализом.

## Ссылки на модули

Для быстрого поиска информации:

- [Карта модулей и dependency graph](modules/overview.md)
- [Core: config, database, security](modules/core-layer.md)
- [Models: 7 SQLAlchemy моделей](modules/models-layer.md)
- [Schemas: Pydantic схемы](modules/schemas-layer.md)
- [Services: бизнес-логика](modules/services-layer.md)
- [API: все эндпоинты и deps](modules/api-layer.md)
- [Web: шаблоны, CSS, JS](modules/web-layer.md)
- [Alembic: миграции](modules/alembic.md)
- [Testing: тесты и fixtures](modules/testing.md)
- [Telegram-bot: статус и план](modules/telegram-bot.md)
- [Docker: инфраструктура](modules/docker-infra.md)