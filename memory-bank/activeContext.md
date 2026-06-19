# Active Context — Chess Tracker

## Current Focus
SSE real-time обновления полностью исправлены и работают.

## Recent Changes (2026-06-19)
- Исправлен корневой баг SSE: `publish_event` теперь yield dict вместо строки
- Добавлены SSE события во все сервисы: player, tournament, game, import
- Исправлен `sse.js`: реконнект перерегистрирует внешние listeners
- Обновлены все шаблоны: dashboard, players, tournament detail, tournaments list
- 193 passed, 0 failed, ruff clean

## Key Decisions
- SSE event format: `{"event": "name", "data": "json_string"}` — совместим с sse-starlette EventSourceResponse
- Event type constants вынесены в `sse_events.py` для консистентности
- TDD подход: тесты написаны до реализации

## Next Steps
- Мониторинг производительности SSE при большом количестве подключений
- Возможные улучшения: SSE heartbeat через EventSource API, а не через data event
