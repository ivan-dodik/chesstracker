# Active Context — Chess Tracker

## Current Focus
Все тесты проходят (202 unit + 76 E2E). E2E тесты исправлены.

## Recent Changes (2026-06-20)
- Исправлены E2E тесты: rate limiting (429), ApexCharts, HX boost навигация
- Кэширование admin токена в conftest.py для избежания 429
- Обновлены тесты на ApexCharts вместо Chart.js
- Тесты навигации: goto вместо click (HX boost)
- 202 passed, 76 E2E passed

## Key Decisions
- SSE event format: `{"event": "name", "data": "json_string"}`
- E2E conftest: session-scoped token caching для rate limiting avoidance
- Тесты читают файлы напрямую из ФС вместо HTTP-запросов

## Next Steps
- Мониторинг производительности SSE
- Возможные улучшения: SSE heartbeat, оптимизация N+1
