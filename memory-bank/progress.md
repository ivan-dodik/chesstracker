# Progress: Chess Tracker

## Текущий статус
**Все майлстоуны M1–M17 завершены.** Дополнительно: CRUD-формы, аутентификация, оптимизации производительности, множество фронтенд-фикс. 189 тестов (160 API/service + 29 E2E), ruff clean. Запланированы M18–M22.

## Что работает
- ✅ **M1: Архитектура и планирование** — полная документация
- ✅ **M2: Окружение и Docker** — Docker Compose, Dockerfile, pyproject.toml
- ✅ **M3: Backend — модели и БД**
  - ✅ Core: config.py (pydantic-settings), database.py (async engine, pool), security.py (JWT, bcrypt)
  - ✅ Модели: User, Player, Tournament, Game, RatingHistory, Favorite, ActivityLog
  - ✅ Alembic: async env.py, миграция "initial" накатана (8 таблиц)
  - ✅ Pydantic схемы: User, Player, Tournament, Game, RatingHistory, Favorite, ActivityLog
  - ✅ Seed: 2 user, 30 players, 10 tournaments, 225 games, 180 rating_history, 4 favorites
  - ✅ bcrypt зафиксирован на 4.0.1 (совместимость с passlib)
- ✅ **M4: Backend — API: аутентификация и базовые CRUD**
- ✅ **M5: Backend — API: специфичные фичи**
- ✅ **M6: Frontend — базовая структура и навигация**
- ✅ **M7: Frontend — дашборд и детальные страницы**
- ✅ **M8: Frontend — фичи** (SSE, избранное, экспорт/импорт CSV)
- ✅ **M9: Telegram-bot** (long-polling, /start, /subscribe, /unsubscribe, notifier)
- ✅ **M10: Тестирование и CI** (ruff clean, pre-commit hook, GitHub Actions CI)
- ✅ **M11: Финальная документация**
- ✅ **M12: TDD-инфраструктура и правила**
- ✅ **M13: API-тесты — Турниры, Игры, Export, Import (~24 теста)**
- ✅ **M14: API-тесты — Activity Log, Health, краевые случаи (~12 тестов)**
- ✅ **M15: Unit-тесты сервисов (~20 тестов)**
- ✅ **M16: Telegram-bot тесты и CI (~6 тестов)**
- ✅ **M17: E2E тесты Playwright (29 тестов)**
- ✅ **CRUD-формы** (create/edit/delete) для players, tournaments, games + 12 web-тестов
- ✅ **Аутентификация всех страниц** (get_current_user_for_web, cookie jwt_token)
- ✅ **Docker entrypoint** — авто-миграции (alembic) + seed при пустой БД
- ✅ **Оптимизации производительности** — N+1 batch, lazy="raise", pool tuning, Jinja2 cache
- ✅ **Фронтенд-фиксы** — hx-boost, Alpine.js/HTMX swap, guards, SSE cleanup
- ✅ **Code review** — 22 замечания исправлены

## Что осталось сделать
- [ ] M18: CSV экспорт auth + debounce фильтрации турниров
- [ ] M19: Расчёт рейтинга (ELO) + RatingHistory
- [ ] M20: SSE real-time — обновление данных на страницах
- [ ] M21: Круговая диаграмма на странице игрока
- [ ] M22: Лог активности — UI-страница + аудит рейтинга
- [ ] Доработка фронтенда (мобильное меню, пустые состояния) — опционально

## Известные проблемы
- **bcrypt 5.x** несовместим с passlib 1.7.4 — зафиксирована версия 4.0.1
- **Jinja2 3.1.x** несовместим со Starlette Jinja2Templates — используется кастомный Environment с cache_size=400
- **hx-boost + Alpine.js** — скрипты шаблонов должны быть в `{% block content %}`, а не в `{% block extra_head %}`
- **Alpine.js + HTMX swap** — `alpine:init` event fired ОДИН раз; компоненты регистрируются напрямую + `Alpine.initTree()` в `htmx:afterSwap`

## Доступные инструменты агента
- **Агентские скиллы Cline**: установлено 32 скилла. Конфигурация: `skills-lock.json`.
  - `use_skill` — активация любого установленного скилла по имени
  - Список всех скиллов: `skills-lock.json` (ключи `skills` → имена скиллов)
  - Индекс: `skills-index.md`
  - Правила документирования: `.clinerules/memory-bank.md`
- **Playwright MCP**: `@executeautomation/playwright-mcp-server` — браузерная автоматизация.
  - MCP-сервер: `github.com/executeautomation/mcp-playwright`
  - Инструменты: `playwright_navigate`, `playwright_screenshot`, `playwright_click` и др.

## Эволюция проектных решений
- **2026-06-06**: Инициализация → M1 (архитектура)
- **2026-06-06 14:17**: M2 — Docker-инфраструктура
- **2026-06-06 14:38**: M3 — модели, миграции, схемы, seed
- **2026-06-06 16:40**: M4 — API: auth + CRUD + тесты 8/8
- **2026-06-06 16:58**: M5 — API: специфичные фичи + тесты 20/20
- **2026-06-06 20:24**: M6 — Frontend: шаблоны, CSS, JS, веб-роуты
- **2026-06-06 20:58**: M7 — дашборд с Chart.js, профили игроков, детали турниров
- **2026-06-06 21:06**: M8 — SSE-клиент, toast-уведомления
- **2026-06-06 21:16**: M9 — Telegram-bot
- **2026-06-06 21:27**: M10 — ruff clean, pre-commit hook, CI
- **2026-06-06 21:34**: M11 — README.md, финальная документация
- **2026-06-07**: CRUD-формы, аутентификация всех страниц, 177 тестов
- **2026-06-07 02:40**: E2E тесты (Playwright) — 29 тестов
- **2026-06-13**: Docker entrypoint — авто-миграции и seed
- **2026-06-14**: Playwright MCP установлен, скиллы оптимизированы (85→32), аудит документации
- **2026-06-14**: Code review — 22 замечания исправлены
- **2026-06-14–15**: Оптимизации (N+1, pool, cache, lazy="raise") + фронтенд-фиксы (hx-boost, Alpine.js guards, SSE cleanup)
- **2026-06-15**: Alpine.js/HTMX swap fix — Alpine.initTree() + скрипты в content blocks
- **2026-06-18**: REPORT_HUMAN.md — человекочитаемый отчёт

## Ссылки на модули
Детальное описание каждого слоя — в соответствующих файлах (см. [полный индекс](index.md)):
- [Backend: все модули](backend/overview.md)
- [Frontend: шаблоны, CSS, JS](frontend/overview.md)
- [Telegram-bot](telegram-bot/overview.md)
- [Testing: тесты](testing/overview.md)
- [Infrastructure: Docker, CI, pre-commit](infrastructure/docker.md)
- [Config: зависимости, env](config/backend-pyproject.md)
- [Meta: баги, security, архитектура](meta/bugs.md)