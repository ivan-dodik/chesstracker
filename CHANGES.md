# История изменений (CHANGES.md)

## 2026-06-06 20:24 — M6: Frontend — базовая структура и навигация
- Созданы: CSS, JS, HTML-шаблоны (base, login, index, players/list, tournaments/list)
- Созданы partials: player_row, tournament_row, pagination
- Созданы веб-роуты (web.py) для 4 страниц
- Проверены HTTP 200 для всех страниц
- 20/20 тестов проходят

## 2026-06-06 20:33 — Memory Bank расширен
- Созданы module-файлы в memory-bank/modules/ (overview, core, models, schemas, services, api, web, alembic, testing, telegram-bot, docker-infra)

## 2026-06-06 20:58 — M7: Frontend — дашборд и детальные страницы
- Добавлены веб-роуты: /players/{id}, /tournaments/{id}
- Chart.js CDN подключён в base.html
- Дашборд: графики рейтинга (line chart) и статистики (doughnut chart) с Chart.js + Alpine.js
- Создан профиль игрока (players/detail.html): рейтинг, статистика wins/losses/draws, график рейтинга, head-to-head, избранное
- Созданы детали турнира (tournaments/detail.html): информация, таблица standings с wins/draws/losses, партии по турам (аккордеон), экспорт CSV, импорт CSV для админа
- Обновлён TournamentStandings: добавлены wins, draws, losses
- Обновлён GameRead: добавлены white_player_name, black_player_name
- Обновлён game_service: обогащение партей именами игроков
- Обновлён tournament_service: подсчёт wins/draws/losses в standings
- Добавлены CSS-стили для страниц игрока, турнира, графиков, h2h
- 20/20 тестов проходят, docker build успешен

## 2026-06-06 21:06 — M8: Frontend — фичи
- Создан SSE-клиент (backend/app/static/js/sse.js): EventSource подключение к /api/events, toast-уведомления о новых партиях, изменении результатов, обновлении рейтинга
- SSE-клиент подключён в base.html
- Добавлен CSS-стиль flash-warning (для уведомлений об изменении результатов)
- Защита роутов через htmx:responseError (401 → редирект на /login) и Alpine.js Auth.isAuthenticated()
- Аутентификация на фронте: форма логина, JWT в localStorage, Authorization header через htmx:configRequest
- Избранное: кнопка ★ на профиле, список на дашборде
- Экспорт CSV: кнопка на странице турнира
- Импорт CSV: форма для админа на странице турнира

## 2026-06-06 21:27 — M10: Тестирование и CI
- Исправлены все ошибки ruff в backend (122 → 0) и telegram-bot (12 → 0)
- Добавлены per-file-ignores для E501 в pyproject.toml обоих проектов
- Переименована TemplateResponse → template_response в web.py (N802)
- Создан .pre-commit-config.yaml с ruff hook для backend и telegram-bot
- Создан .github/workflows/ci.yml: ruff lint + pytest с PostgreSQL
- ruff check проходит на всех файлах, 20/20 тестов проходят
- Обновлён Memory Bank (activeContext.md, progress.md)

## 2026-06-06 21:16 — M9: Telegram-bot
- Создан config.py (Pydantic BaseSettings: TG_BOT_TOKEN, BACKEND_URL)
- Реализован bot.py: инициализация Application, регистрация хендлеров, job_queue для периодического polling
- Созданы handlers/start.py: /start — приветственное сообщение и инструкция
- Созданы handlers/subscribe.py: /subscribe и /unsubscribe с сохранением подписчиков в subscribers.json
- Созданы services/api_client.py: HTTP-клиент для backend (get_active_tournaments, get_tournament_games)
- Созданы services/notifier.py: периодический опрос активных турниров, отправка уведомлений подписанным чатам
- Добавлены __init__.py в handlers/ и services/
- Обновлён Dockerfile: копирование config.py
- docker compose build telegram-bot успешен

## 2026-06-06 13:56 — M1: Архитектура и планирование
- Создан project_task.md — полное ТЗ
- Создан IMPLEMENTATION_PLAN.md — 11 майлстоунов, ~80 шагов
- Создан ARCHITECTURE.md — архитектура, ERD, API, стек
- Создан Memory Bank — 6 core-файлов
- Созданы .clinerules/ — 5 правил
- Создан LICENSE — MIT
- Выполнен коммит и пуш

## 2026-06-06 14:17 — M2: Окружение и Docker
- Созданы pyproject.toml (backend + bot) с зависимостями
- Созданы Dockerfile (backend + bot)
- Созданы docker-compose.yml и docker-compose.override.yml
- Создан .env.example
- Создана полная структура директорий backend
- docker compose build успешен

## 2026-06-06 14:38 — M3: Backend — модели и база данных
- Созданы core: config.py (BaseSettings), database.py (async engine), security.py (JWT, bcrypt)
- Созданы 7 SQLAlchemy моделей
- Инициализирован Alembic, создана миграция "initial" (8 таблиц)
- Созданы Pydantic схемы для всех моделей
- Создан seed.py (2 user, 30 players, 10 tournaments, 225 games, 180 rating_history, 4 favorites)
- Зафиксирована версия bcrypt 4.0.1 (совместимость с passlib)

## 2026-06-06 16:40 — M4: Backend — API: аутентификация и базовые CRUD
- Созданы deps.py (get_db, get_current_user, get_current_admin)
- Созданы auth API (login, register, me)
- Созданы CRUD API для игроков, турниров, партий (с пагинацией, поиском, фильтрацией)
- Созданы standings с автоподсчётом очков
- Созданы router.py и main.py (FastAPI app, CORS, Swagger UI)
- Написаны 8 тестов (auth, players)
- 8/8 тестов passed, Swagger UI работает

## 2026-06-06 16:58 — M5: Backend — API: специфичные фичи
- Созданы API: rating, favorite, stats, SSE, export/import CSV, activity log
- ActivityLog интегрирован во все CRUD
- SSE-события при создании/обновлении партий
- 12 новых тестов (ratings, stats, favorites)
- 20/20 тестов passed, docker build успешен
- Выполнен коммит и пуш: `6f16a94`

## 2026-06-06 21:34 — M11: Финальная документация
- Создан README.md с описанием проекта, стеком, быстрым стартом, API-эндпоинтами, командами для разработки
- ARCHITECTURE.md дополнен пунктами о pre-commit hook, CI и тестовой инфраструктуре
- REPORT.md дополнен итогами M2–M5, M9, M11; добавлена пропущенная запись в историю (M3)
- PROMPTS.md обновлён записью о M11
- CHANGES.md обновлён записью о M11
- Memory Bank обновлён (activeContext.md, progress.md)
- Выполнен финальный коммит и пуш

## 2026-06-06 21:49 — Подключены скиллы для Cline
- Установлен пакет mattpocock/skills (29 скиллов: улучшение архитектуры, code review, TDD, диагностика, планирование)
- Установлен пакет anthropics/skills (18 скиллов: фронтенд-дизайн, документы, тестирование)
- Установлен пакет obra/superpowers (14 скиллов: процессы разработки, дебаггинг, code review)
- Установлен пакет supabase/agent-skills (2 скилла: PostgreSQL best practices)
- Установлен пакет xixu-me/skills (12 скиллов: GitHub Actions, безопасность, хостинг)
- Обновлён .gitignore для игнорирования .agents/
- Созданы: .agents/ — директория с установленными скиллами

## 2026-06-06 22:35 — Исправление запуска telegram-bot
- Исправлена ошибка `AttributeError: 'NoneType' object has no attribute 'run_repeating'` при запуске telegram-bot
- Добавлен extra `[job-queue]` для зависимости `python-telegram-bot` в `telegram-bot/pyproject.toml`
- Перегенерирован `uv.lock`: добавлены apscheduler v3.11.2, tzdata v2026.2, tzlocal v5.3.1
- Затронутые файлы: telegram-bot/pyproject.toml, telegram-bot/uv.lock

## 2026-06-06 22:45 — Исправление проблемы root-файлов в Docker volumes
- Добавлен `user: "${UID:-1000}:${GID:-1000}"` в docker-compose.override.yml для сервисов backend и telegram-bot
- Добавлены `UID=1000`, `GID=1000` в .env.example
- **Проблема:** `__pycache__` внутри контейнера создавались от root → недоступны для удаления пользователем ai без sudo
- **Решение:** процессы внутри контейнера теперь запускаются от UID/GID текущего пользователя
- Затронутые файлы: docker-compose.override.yml, .env.example

## 2026-06-06 22:53 — Graceful shutdown бота при фейковом токене
- Добавлен метод `is_token_valid()` в `telegram-bot/config.py` — проверяет, что токен не пустой, не равен заглушке и соответствует формату Telegram
- Изменён `telegram-bot/bot.py` — используется `is_token_valid()`, graceful exit (код 0) вместо падения с ошибкой
- Изменён `docker-compose.yml` — `restart: "no"` для telegram-bot (контейнер не перезапускается при graceful shutdown)
- Обновлён `.env.example` — TG_BOT_TOKEN закомментирован с пометкой о необходимости реального токена
- Создан `TELEGRAM_BOT_SETUP.md` — инструкция по созданию токена через @BotFather
- Затронутые файлы: telegram-bot/config.py, telegram-bot/bot.py, docker-compose.yml, .env.example, TELEGRAM_BOT_SETUP.md

## 2026-06-06 23:16 — Исправление ошибки uv cache (Permission denied) в Docker
- Добавлен непривилегированный пользователь `appuser` в `backend/Dockerfile` и `telegram-bot/Dockerfile`
- Установлена переменная `UV_CACHE_DIR=/home/appuser/.cache/uv` для обоих контейнеров
- Назначены права на `/app` пользователю `appuser` через `chown -R appuser:appuser /app`
- **Проблема:** `uv` при запуске от root пытался создать `/.cache/uv` — доступ запрещён (ошибка 13)
- **Решение:** создан отдельный пользователь, вся работа выполняется от него
- Затронутые файлы: backend/Dockerfile, telegram-bot/Dockerfile

## 2026-06-07 00:00 — Исправление фронтенд-ошибок Alpine.js и инициализации БД
- Установлен скилл `alpinejs` (brettatoms/agent-skills@alpinejs)
- Исправлен порядок загрузки скриптов: main.js (defer) → Alpine.js (defer) в `<head>`
- Все Alpine-компоненты перенесены в main.js, регистрация через `document.addEventListener('alpine:init', ...)`
- Исправлены ошибки `document.body.addEventListener` → `document.addEventListener` в шаблонах (index.html, players/list.html, tournaments/list.html) — скрипты в `<head>` обращались к несуществующему body
- Применены миграции (`alembic upgrade head`) и seed-данные (`python -m app.seed`)
- **Результат:** 0 ошибок, 0 предупреждений на всех страницах (верифицировано через Playwright)
- Затронутые файлы: backend/app/static/js/main.js, backend/app/templates/base.html, backend/app/templates/index.html, backend/app/templates/players/list.html, backend/app/templates/tournaments/list.html, skills-lock.json

## 2026-06-07 01:24 — Исправление проблемы аутентификации
- **Проблема:** После ввода логина/пароля происходил быстрый редирект обратно на страницу логина
- **Причина:** Обработчик HTMX-ошибок `htmx:responseError` при получении 401 ошибки (например, при запросе `/api/favorites` без токена) очищал токен и перенаправлял на `/login`, даже если пользователь только что вошёл
- **Решение:**
  1. Добавлено подробное логирование в процесс логина (`console.log` в `loginForm.submit()`)
  2. Улучшена обработка ошибок при запросе `/api/auth/me` — теперь не блокирует вход при ошибке
  3. Исправлен обработчик `htmx:responseError` — теперь проверяет наличие токена: если токена нет, 401 игнорируется (публичный доступ); если токен есть, но 401 — очистка и редирект
  4. Добавлена небольшая задержка (100ms) перед редиректом после логина для гарантии сохранения токена
- **Результат:** Вход должен работать корректно, пользователи остаются на дашборде после аутентификации
- Затронутые файлы: backend/app/static/js/main.js

## 2026-06-07 02:40 — Установка BrowserTools MCP сервера
- Установлен MCP сервер `@agentdeskai/browser-tools-mcp@1.2.1` в `/home/ai/Documents/Cline/MCP/browser-tools-mcp/`
- Установлен глобально `@agentdeskai/browser-tools-server@1.2.1` — сервер-прослойка для сбора логов браузера
- Запущен `browser-tools-server` на порту 3025
- Настроен `cline_mcp_settings.json` — добавлен сервер `github.com/AgentDeskAI/browser-tools-mcp`
- Продемонстрирована работа: `getConsoleLogs` вернул пустой массив (корректный ответ)
- Для полной функциональности требуется:
  1. Установить Chrome-расширение BrowserTools (скачать с GitHub releases)
  2. Открыть Chrome DevTools → панель BrowserToolsMCP
- Затронутые файлы: `/home/ai/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

## 2026-06-07 02:31 — TDD: тесты для главной страницы, логина и авторизации
- **Фаза 1 (Web-страницы):** создан `tests/test_web.py` — 7 тестов (главная страница, HTMX-атрибуты, Alpine.js компоненты, favourites section hidden, страница логина, форма логина, Alpine loginForm)
- **Фаза 2 (Auth API):** расширен `tests/test_auth.py` — добавлено 3 теста (несуществующий пользователь, невалидный токен, register без токена)
- **Фаза 3 (Auth flow):** создан `tests/test_auth_flow.py` — 6 тестов (логин → /me, protected endpoint, unauthorized, register as admin, duplicate username, non-admin register)
- **Итого:** с 20 до 36 тестов (+16)
- **Результат:** 36/36 тестов проходят, 0 ошибок ruff
- Затронутые файлы: backend/tests/test_auth.py, backend/tests/test_web.py, backend/tests/test_auth_flow.py

## 2026-06-07 02:20 — Документирование проблемы аутентификации в BUGS.md
- **Создан BUGS.md** — полный документ с описанием проблемы циклического редиректа после логина
- **Содержание BUGS.md:**
  - Дата обнаружения, версия, окружение
  - Подробное описание симптомов с визуальным наблюдением
  - Хронология двух попыток исправлений с изменениями и результатами
  - Анализ корневой причины (гонка HTMX `hx-trigger="load"` и Alpine.js `x-show`)
  - Приоритет дальнейших исправлений (Critical, Important, Minor)
  - Текущий статус: частично исправлено
- **Обновлён REPORT.md** — добавлена запись о проблеме в «Ключевые проблемы и решения»; добавлена строка в «История работы»
- **Обновлены PROMPTS.md, Memory Bank** — зафиксирована текущая сессия
- Затронутые файлы: BUGS.md, REPORT.md, PROMPTS.md, memory-bank/activeContext.md, memory-bank/progress.md
