# Правило использования агентских скиллов

## Always-On: Caveman Mode

**Скилл `caveman` активен ПОСТОЯННО.** Каждый ответ агента должен быть в компактном стиле:

### Правила компактного стиля

- **Удалять:** артикли (a/an/the), филлеры (just/really/basically/actually/simply), вежливости (sure/certainly/of course), хеджирование
- **Фрагменты допустимы.** Короткие синонимы (big → not extensive, fix → not "implement a solution")
- **Аббревиатуры:** DB/auth/config/req/res/fn/impl
- **Стрелки для причинности:** X → Y
- **Паттерн:** `[thing] [action] [reason]. [next step].`

### Примеры

**НЕПРАВИЛЬНО:**
> Sure! I'd be happy to help you with that. The issue you're experiencing is likely caused by...

**ПРАВИЛЬНО:**
> Bug in auth middleware. Token expiry check use `<` not `<=`. Fix:

### Исключения (временно отключать caveman)

- Security warnings — полные предупреждения
- Irreversible ops — подтверждения деструктивных действий
- Multi-step sequences — где порядок критичен
- Пользователь просит уточнить / повторяет вопрос
- **Документационные файлы** — `CHANGES.md`, `PROMPTS.md`, `REPORT.md`, `memory-bank/`, `.clinerules/`: пишем подробно, с полными описаниями и примерами. Caveman-стиль только для кода и ответов пользователю.

После исключения — вернуться к компактному стилю.

**Выкл:** только по команде "stop caveman" / "normal mode".

---

## Порядок активации скиллов

При получении задачи агент **обязан**:

1. **Проверить триггеры** в `skills-index.md`
2. **Активировать** `use_skill` с нужным скиллом ДО начала реализации
3. **Не активировать** скиллы, которые не релевантны текущей задаче

### Приоритеты при конфликте

| Конфликт | Решение |
|----------|---------|
| `tdd` vs `python-testing` | Использовать оба: `tdd` для процесса, `python-testing` для specifics pytest |
| `brainstorming` vs `writing-plans` | `brainstorming` → exploration, `writing-plans` → конкретный план |
| `design-an-interface` vs `improve-codebase-architecture` | `design-an-interface` → новый модуль, `improve-codebase-architecture` → рефакторинг |
| `dispatching-parallel-agents` vs `subagent-driven-development` | `dispatching` → 2+ независимых задач, `subagent-driven` → серия параллельных итераций |

### Маппинг контекст → скилл

| Задача | Скилл(ы) |
|--------|----------|
| Новый API endpoint | `fastapi-python` → `tdd` → `verification-before-completion` |
| Исправление бага | `diagnose` → `tdd` → `verification-before-completion` |
| UI/шаблон | `frontend-design` + `htmx` / `alpinejs` |
| Миграция БД | `postgresql-best-practices` |
| Docker/deployment | `docker` |
| Code review | `review` |
| Новая фича (сложная) | `brainstorming` → `writing-plans` → `executing-plans` |
| Завершение ветки | `finishing-a-development-branch` → `verification-before-completion` |
| Архитектурное улучшение | `zoom-out` → `improve-codebase-architecture` |
| E2E тесты | `webapp-testing` (pytest + Playwright) |
| Browser/скриншоты | **Playwright MCP** (`playwright_navigate`, `playwright_screenshot`, `playwright_click`) |
| CI/CD | `github-actions-docs` |
| Документация | `doc-coauthoring` |
| Параллельные задачи | `dispatching-parallel-agents` |
| Конец сессии | `handoff` |

---

## Справочник

Полный каталог скиллов → `skills-index.md`