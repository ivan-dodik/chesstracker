# Active Context: Chess Tracker

## Текущее состояние проекта
Проект полностью реализован. Задокументирована проблема с циклическим редиректом после логина (см. BUGS.md).

## Последние изменения
- **Установлен MCP Browser Tools (02:40)**: `@agentdeskai/browser-tools-mcp@1.2.1`, `@agentdeskai/browser-tools-server@1.2.1`, порт 3025
- **Проверена форма логина через MCP Browser Tools (03:15)**: в реальном Chrome — логин admin/admin123 → редирект на дашборд → все API 200 OK → 0 ошибок → аудит доступности 80/100
- Исправлены фронтенд-ошибки Alpine.js (порядок загрузки скриптов, defer, alpine:init)
- **Исправлена проблема аутентификации (01:24)**: обработчик `htmx:responseError` теперь проверяет наличие токена, добавлено логирование
- **Создан BUGS.md (02:20)**: полная документация проблемы циклического редиректа после логина с хронологией исправлений, анализом корневой причины и приоритетом дальнейших работ

## Следующие шаги
- Исправить контрастность цветов CSS (цвет ссылок `#3498db`, placeholder-текст `#7f8c8d`) — результат аудита доступности Score 80/100
- Добавить `<label>` к select элементам на дашборде
- Устранить гонку между HTMX `hx-trigger="load"` и Alpine.js `x-show` на дашборде (защищённые эндпоинты отправляют запросы до того, как Alpine скрыл секции для неаутентифицированных пользователей)
- Альтернатива: заменить `hx-trigger="load"` на Alpine-управляемую загрузку для защищённых секций

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
- **MCP Browser Tools**: установлен `@agentdeskai/browser-tools-mcp@1.2.1` с Chrome-расширением. Инструменты: `takeScreenshot`, `getConsoleLogs`, `getConsoleErrors`, `getNetworkErrors`, `getNetworkLogs`, `runAccessibilityAudit`. Сервер работает на порту 3025.
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