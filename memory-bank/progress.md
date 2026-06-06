# Progress: Chess Tracker

## Текущий статус
**M15: Unit-тесты сервисов** завершён. Проект полностью реализован. Добавлены unit-тесты для всех сервисов (21 тест). Тестовая база: 95 тестов.
Документирована проблема с циклическим редиректом после логина (см. BUGS.md).

## Что работает
- ✅ **M1: Архитектура и планирование** — полная документация
- ✅ **M2: Окружение и Docker** — Docker Compose, Dockerfile, pyproject.toml
- ✅ **M3: Backend — модели и БД**
  - ✅ Core: config.py (pydantic-settings), database.py (async engine), security.py (JWT, bcrypt)
  - ✅ Модели: User, Player, Tournament, Game, RatingHistory, Favorite, ActivityLog
  - ✅ Alembic: async env.py, миграция "initial" накатана (8 таблиц)
  - ✅ Pydantic схемы: User, Player, Tournament, Game, RatingHistory, Favorite, ActivityLog
  - ✅ Seed: 2 user, 30 players, 10 tournaments, 225 games, 180 rating_history, 4 favorites
  - ✅ bcrypt зафиксирован на 4.0.1 (совместимость с passlib)
- ✅ **M4: Backend — API: аутентификация и базовые CRUD**
- ✅ **M5: Backend — API: специфичные фичи**
- ✅ **M6: Frontend — базовая структура и навигация**
- ✅ **M7: Frontend — дашборд и детальные страницы**
- ✅ **M8: Frontend — фичи**
- ✅ **M9: Telegram-bot**
- ✅ **M10: Тестирование и CI**
  - ✅ ruff: все ошибки в backend (122) и telegram-bot (12) исправлены
  - ✅ .pre-commit-config.yaml: ruff hook для backend и telegram-bot
  - ✅ .github/workflows/ci.yml: ruff lint + pytest с PostgreSQL
  - ✅ ruff check проходит на всех файлах
  - ✅ 20/20 тестов проходят
- ✅ **M11: Финальная документация**
  - ✅ README.md создан
  - ✅ ARCHITECTURE.md дополнен
  - ✅ REPORT.md проверен и дополнен (все майлстоуны, история работы)
  - ✅ PROMPTS.md проверен и дополнен
  - ✅ CHANGES.md проверен и дополнен (все майлстоуны)
  - ✅ Memory Bank обновлён

## Что осталось сделать
- [ ] Исправить контрастность цветов CSS (результат аудита доступности Score 80/100)
- [ ] Добавить `<label>` к select элементам на дашборде
- [ ] Устранить гонку между HTMX `hx-trigger="load"` и Alpine.js `x-show` на дашборде
- [ ] Увеличить задержку перед редиректом после логина (100ms → 300ms) или перейти на Promise-based подход

## Известные проблемы
- **bcrypt 5.x** несовместим с passlib 1.7.4 — зафиксирована версия 4.0.1
- **Jinja2 3.1.x** несовместим со Starlette Jinja2Templates — используется кастомный Environment с cache_size=0
- **Циклический редирект после логина** — частично исправлено. Корневая причина: гонка между HTMX `hx-trigger="load"` и Alpine.js `x-show`. При входе на дашборд HTMX-запросы к защищённым эндпоинтам (например, `/api/favorites`) могут уйти до того, как Alpine скроет секции для неаутентифицированных пользователей. Если запрос возвращает 401, старый обработчик `htmx:responseError` очищал токен и редиректил на `/login`. Исправлено: добавлено условие `&& localStorage.getItem('jwt_token')` в обработчик, улучшена обработка `/api/auth/me`, добавлена задержка 100ms. **Полный анализ: BUGS.md.**

## Доступные инструменты агента
- **Агентские скиллы Cline**: установлены 5 пакетов (75+ скиллов). Конфигурация: `skills-lock.json`.
  - `use_skill` — активация любого установленного скилла по имени
  - Список всех скиллов: `skills-lock.json` (ключи `skills` → имена скиллов)
  - Правила документирования при установке скиллов: `.clinerules/memory-bank.md`
- **MCP Browser Tools**: `@agentdeskai/browser-tools-mcp@1.2.1` с Chrome-расширением.
  - Сервер: порт 3025, процесс: `browser-tools-server`
  - Инструменты: `takeScreenshot`, `getConsoleLogs`, `getConsoleErrors`, `getNetworkErrors`, `getNetworkLogs`, `runAccessibilityAudit`, `runPerformanceAudit`, `runSEOAudit`
  - Настройки: `cline_mcp_settings.json`
  - **Проверка формы логина (03:15)**: логин admin/admin123 → редирект на дашборд → все API 200 OK → 0 ошибок → аудит 80/100

## Эволюция проектных решений
- **2026-06-06**: Инициализация
- **2026-06-06 13:35**: IMPLEMENTATION_PLAN, архитектурные решения
- **2026-06-06 14:17**: M2 завершён — Docker-инфраструктура
- **2026-06-06 14:38**: M3 завершён — модели, миграции, схемы, seed
- **2026-06-06 16:40**: M4 завершён — API: auth + CRUD + тесты 8/8
- **2026-06-06 16:58**: M5 завершён — API: специфичные фичи + тесты 20/20
- **2026-06-06 20:24**: M6 завершён — Frontend: шаблоны, CSS, JS, веб-роуты
- **2026-06-06 20:33**: Memory Bank расширен — созданы module-файлы
- **2026-06-06 20:58**: M7 завершён — дашборд с Chart.js, профили игроков, детали турниров
- **2026-06-06 21:06**: M8 завершён — SSE-клиент, toast-уведомления, CSS flash-warning
- **2026-06-06 21:16**: M9 завершён — Telegram-bot (long-polling, /start, /subscribe, /unsubscribe, notifier)
- **2026-06-06 21:27**: M10 завершён — ruff clean, pre-commit hook, GitHub Actions CI
- **2026-06-06 21:34**: M11 завершён — README.md, финальная проверка документации, коммит и пуш
- **2026-06-07 00:00**: Исправлены Alpine.js ошибки (порядок загрузки скриптов)
- **2026-06-07 01:24**: Исправлена проблема аутентификации (htmx:responseError, логирование)
- **2026-06-07 02:20**: Создан BUGS.md — полная документация проблемы циклического редиректа после логина
- **2026-06-07 02:40**: Установлен MCP Browser Tools (`browser-tools-mcp`, `browser-tools-server` v1.2.1)
- **2026-06-07 03:15**: Проверена форма логина через MCP Browser Tools в реальном Chrome — аутентификация работает корректно

## Ссылки на модули
Детальное описание каждого слоя — в соответствующих файлах (см. [полный индекс](index.md)):
- [Backend: все модули](backend/overview.md)
- [Frontend: шаблоны, CSS, JS](frontend/overview.md)
- [Telegram-bot](telegram-bot/overview.md)
- [Testing: 36 тестов](testing/overview.md)
- [Infrastructure: Docker, CI, pre-commit](infrastructure/docker.md)
- [Config: зависимости, env](config/backend-pyproject.md)
- [Meta: баги, security, архитектура](meta/bugs.md)
