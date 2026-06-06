# TDD: Test-Driven Development

## Философия

**Основной принцип**: Тесты должны проверять поведение через публичные интерфейсы, а не детали реализации. Код может полностью измениться; тесты не должны.

**Хорошие тесты** — интеграционные: они исполняют реальные пути кода через публичные API. Они описывают *что* система делает, а не *как*.

**Плохие тесты** — привязаны к реализации. Сигнал: тест ломается при рефакторинге, хотя поведение не изменилось.

## 1. Red-Green-Refactor

- **Red**: Перед реализацией новой функции → написать падающий тест
- **Green**: Реализовать минимальный код для прохождения теста
- **Refactor**: Отрефакторить, сохраняя зелёные тесты
- **Никогда не рефакторить в Red** — сначала добейся зелёного

Для уже существующего кода (как в этом проекте) фаза Red означает: написать тест, убедиться что он падает без тестируемого кода, затем убедиться что он проходит с существующей реализацией.

## 2. Вертикальные срезы (Tracer Bullet)

Пиши тесты вертикальными срезами, а не горизонтальными слоями:

```
НЕПРАВИЛЬНО (горизонтально):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

ПРАВИЛЬНО (вертикально):
  RED→GREEN: test1→impl1
  RED→GREEN: test2→impl2
  RED→GREEN: test3→impl3
```

## 3. Маппинг файлов → тесты

При изменении файла запускать соответствующие тесты:

| Изменённый файл | Запустить тесты |
|----------------|-----------------|
| `app/api/auth.py` | `tests/test_auth.py`, `tests/test_auth_flow.py` |
| `app/api/players.py` | `tests/test_players.py` |
| `app/api/tournaments.py` | `tests/test_tournaments.py` |
| `app/api/games.py` | `tests/test_games.py` |
| `app/api/ratings.py` | `tests/test_ratings.py` |
| `app/api/stats.py` | `tests/test_stats.py` |
| `app/api/favorites.py` | `tests/test_favorites.py` |
| `app/api/activity_log.py` | `tests/test_activity_log.py` |
| `app/api/export.py` | `tests/test_export.py` |
| `app/api/import_route.py` | `tests/test_import_route.py` |
| `app/api/sse.py` | `tests/test_health.py` (health check SSE endpoint) |
| `app/api/web.py` | E2E тесты (`tests/e2e/`) |
| `app/services/*.py` | Соответствующий `tests/services/test_*.py` |
| `app/models/*.py` или `app/schemas/*.py` | Все тесты |
| `tests/conftest.py` | Все тесты |
| Любой файл в `telegram-bot/` | `cd telegram-bot && uv run pytest -v` |

## 4. Критерии завершения задачи

Задача не считается выполненной, пока не пройдены:

1. **Все тесты, связанные с изменёнными файлами** (по таблице выше)
2. **Полный прогон backend**:
   ```bash
   cd backend && uv run pytest -v
   ```
   Результат: 0 failed, 0 errors
3. **Полный прогон telegram-bot** (если были изменения в `telegram-bot/`):
   ```bash
   cd telegram-bot && uv run pytest -v
   ```
4. **Ruff check** без ошибок:
   ```bash
   cd backend && uv run ruff check && cd ../telegram-bot && uv run ruff check
   ```

## 5. Документирование после завершения

Перед `attempt_completion` выполнить:

1. Обновить `CHANGES.md` — дата, время, описание изменений, затронутые файлы
2. Обновить `PROMPTS.md` — если были новые промпты
3. Обновить `REPORT.md` — запись в «Историю работы», «Ключевые проблемы и решения»
4. Обновить Memory Bank (activeContext.md, progress.md)
5. `git add -A && git commit -m "<тип>: <описание>" && git push`

## 6. Pre-commit проверка

Pre-commit hook запускает:
- `ruff check` для backend и telegram-bot
- `pytest` для backend (если есть изменения в backend/)

Коммит блокируется, если:
- Ruff нашёл ошибки
- Тесты не проходят