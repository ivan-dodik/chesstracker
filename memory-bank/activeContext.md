# Active Context: Chess Tracker

## Текущее состояние проекта
Завершён **M3: Backend — модели и база данных**. Созданы все модели, миграции, схемы и seed-данные.

## Последние изменения
- Создан `backend/app/core/config.py` — pydantic-settings
- Создан `backend/app/core/database.py` — async engine + get_db
- Создан `backend/app/core/security.py` — hash_password, JWT
- Созданы SQLAlchemy модели: User, Player, Tournament, Game, RatingHistory, Favorite, ActivityLog
- Настроен Alembic (async), первая миграция накатана
- Созданы Pydantic схемы для всех моделей
- Создан `backend/app/seed.py` — 2 пользователя, 30 игроков, 10 турниров, 258 партий, 180 RatingHistory
- Фикс: bcrypt понижен до 4.0.1 для совместимости с passlib

## Следующие шаги (приоритетный порядок)
1. ✅ **M1: Архитектура и планирование** — выполнено
2. ✅ **M2: Окружение и Docker** — выполнено
3. ✅ **M3: Backend — модели и БД** — выполнено
4. **M4: Backend — API: аутентификация и базовые CRUD**
   - deps.py (get_db, get_current_user, get_current_admin)
   - auth.py (login, register, me)
   - players.py CRUD, tournaments.py CRUD, games.py CRUD
   - router.py, main.py
   - Тесты (3-4)
5. **M5: Backend — API: специфичные фичи** (рейтинг, статистика, SSE, CSV, лог)
6. **M6: Frontend — базовая структура и навигация** (Jinja2, HTMX)
7. **M7: Frontend — дашборд и детальные страницы** (Chart.js, Alpine.js)
8. **M8: Frontend — фичи** (избранное, SSE, CSV, аутентификация)
9. **M9: Telegram-bot** (long-polling)
10. **M10: Тестирование и CI** (GitHub Actions, ruff, pytest)
11. **M11: Финальная документация** (README.md, REPORT.md)

## Активные решения и considerations
- **bcrypt**: зафиксирована версия 4.0.1 из-за несовместимости passlib с bcrypt 5.x
- **Alembic**: настроен на async режим через asyncio.run()
- **Seed-данные**: пересоздают таблицы (drop_all + create_all) при каждом запуске
- Все остальные решения из M1/M2 остаются в силе