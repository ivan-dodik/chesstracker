# Active Context — Chess Tracker

## Current Focus
Проект сдан преподавателю. Текущая работа — рефакторинг процесса разработки: уборка документации, обновление Memory Bank, добавление шага консолидации.

## Recent Changes (2026-06-24)
- Проведён полный аудит документации
- Убраны дублирующие файлы из корня (3 отчёта → 1, 2 плана → 1)
- Артефакты перемещены в docs/
- Удалён memory-bank/meta/ (дублировал корневые документы)
- Memory Bank обновлён: исправлены ссылки, данные, добавлены новые компоненты

## Key Decisions
- ЕДИНСТВЕННЫЙ отчёт: REPORT.md (автоматический) + REPORT_HUMAN.md (ручной, не трогать)
- ЕДИНСТВЕННЫЙ план: IMPLEMENTATION_PLAN.md
- Архивные документы: docs/ (CODE_REVIEW, SECURITY_AUDIT, BUGS, тесты)
- Memory Bank: core-файлы + модульные файлы по директориям (backend/, frontend/, testing/, etc.)
- Правило: агент ОБЯЗАН читать index.md + модульный файл перед работой с кодом

## Key Technical Notes
- SSE event format: `{"event": "name", "data": "json_string"}`
- ApexCharts (не Chart.js) для графиков
- E2E conftest: session-scoped token caching для rate limiting avoidance
- Тесты: 202 unit/integration + 76 E2E = 278 всего

## Next Steps
- Добавить шаг консолидации в процесс (.clinerules/)
- Обновить правила чтения Memory Bank
- Проверить актуальность всех модульных файлов