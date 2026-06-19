# Implementation Plan: Fix SSE Real-Time Updates

## [Overview]

Fix broken Server-Sent Events (SSE) system so real-time notifications work across all connected browser tabs. The root cause is incorrect message formatting in the backend that double-encodes data and strips event names, combined with missing SSE event publishing in several service methods and lost frontend listeners on reconnection.

## [Types]

New SSE event type constants (to avoid stringly-typed event names):

```python
# backend/app/services/sse_events.py (NEW FILE)
class SSEEvents:
    """SSE event type constants."""
    # Player events
    PLAYER_CREATED = "player_created"
    PLAYER_UPDATED = "player_updated"
    PLAYER_DELETED = "player_deleted"

    # Tournament events
    TOURNAMENT_CREATED = "tournament_created"
    TOURNAMENT_UPDATED = "tournament_updated"
    TOURNAMENT_DELETED = "tournament_deleted"

    # Game events
    GAME_CREATED = "game_created"
    GAME_UPDATED = "game_updated"
    GAME_DELETED = "game_deleted"

    # Rating events
    RATING_UPDATED = "rating_updated"
```

All `publish_event` calls will use `event_type: str` parameter matching these constants. The `data` dict payload varies per event type:

| Event Type | Data Fields |
|---|---|
| `player_created` / `player_updated` / `player_deleted` | `player_id`, `player_name`, `rating`, `city` |
| `tournament_created` / `tournament_updated` / `tournament_deleted` | `tournament_id`, `tournament_name`, `status` |
| `game_created` / `game_updated` / `game_deleted` | `game_id`, `tournament_id`, `result`, `white_player_name`, `black_player_name` |
| `rating_updated` | `player_id`, `player_name`, `old_rating`, `new_rating` |

## [Files]

### New files
- `backend/app/services/sse_events.py` — SSE event type constants
- `backend/tests/test_sse_service.py` — Unit tests for SSE service
- `backend/tests/test_sse_events.py` — Unit tests for SSE event constants
- `backend/tests/test_player_sse.py` — Unit tests for player SSE events
- `backend/tests/test_tournament_sse.py` — Unit tests for tournament SSE events
- `backend/tests/test_game_sse.py` — Unit tests for game SSE events
- `backend/e2e/test_sse_realtime_e2e.py` — Comprehensive E2E SSE tests

### Modified files (backend)
- `backend/app/services/sse_service.py` — Fix `publish_event` to yield dicts with `event` + `data` keys
- `backend/app/api/sse.py` — No changes needed (already yields whatever queue returns)
- `backend/app/services/player_service.py` — Add `publish_event` calls to create/update/delete
- `backend/app/services/tournament_service.py` — Add `publish_event` calls to create/update/delete
- `backend/app/services/game_service.py` — Rename event type, add delete event
- `backend/app/services/import_service.py` — Add `publish_event` after bulk import

### Modified files (frontend)
- `backend/app/static/js/sse.js` — Fix reconnection to re-register external listeners
- `backend/app/templates/index.html` — Add game event listeners
- `backend/app/templates/players/list.html` — Add SSE auto-refresh
- `backend/app/templates/tournaments/detail.html` — Fix Alpine.js access + listeners
- `backend/app/templates/tournaments/list.html` — Add SSE auto-refresh

### Test files modified
- `backend/e2e/test_m20_sse_realtime.py` — Update for new event types

## [Functions]

### Modified functions

**`sse_service.py`:**
- `publish_event(event_type, data)` — Return dict `{"event": event_type, "data": json.dumps(...)}` instead of pre-formatted string.

**`player_service.py`:**
- `create_player()` — Add `publish_event(SSEEvents.PLAYER_CREATED, ...)`
- `update_player()` — Add `publish_event(SSEEvents.PLAYER_UPDATED, ...)` + `publish_event(SSEEvents.RATING_UPDATED, ...)` on rating change
- `delete_player()` — Add `publish_event(SSEEvents.PLAYER_DELETED, ...)`

**`tournament_service.py`:**
- `create_tournament()` — Add `publish_event(SSEEvents.TOURNAMENT_CREATED, ...)`
- `update_tournament()` — Add `publish_event(SSEEvents.TOURNAMENT_UPDATED, ...)`
- `delete_tournament()` — Add `publish_event(SSEEvents.TOURNAMENT_DELETED, ...)`

**`game_service.py`:**
- `update_game_result()` — Rename event `"game_result_updated"` → `"game_updated"`
- `delete_game()` — Add `publish_event(SSEEvents.GAME_DELETED, ...)`

**`import_service.py`:**
- `import_tournament_csv()` — Add single `publish_event("games_imported", ...)` after import

**`sse.js` — `SSEClient`:**
- `on()` — Remove direct addEventListener; store only in `_externalListeners`
- `connect()` — Call `_reconnectExternalListeners()` after setup
- New `_reconnectExternalListeners()` — Re-register all external listeners

## [Classes]

No new classes. `SSEClient` gets method additions.

## [Dependencies]

No new dependencies.

## [Testing]

**TDD approach**: Write tests FIRST, then implement.

### Unit tests

**`tests/test_sse_service.py`** (NEW):
- `test_publish_event_returns_dict` — dict with `event` and `data` keys
- `test_publish_event_data_is_json_string` — data is valid JSON
- `test_publish_event_sets_event_type` — event matches event_type param
- `test_subscribe_returns_queue` — subscribe returns asyncio.Queue
- `test_unsubscribe_removes_queue` — queue removed after unsubscribe
- `test_publish_to_subscribers` — subscribe → publish → queue has message
- `test_publish_to_all_subscribers` — subscribe("all") → publish → queue has message

**`tests/test_sse_events.py`** (NEW):
- `test_all_event_types_are_strings` — all attributes are non-empty strings
- `test_no_duplicate_event_types` — all values unique

**`tests/test_player_sse.py`** (NEW):
- `test_create_player_publishes_event`
- `test_update_player_publishes_event`
- `test_update_player_rating_publishes_rating_event`
- `test_delete_player_publishes_event`

**`tests/test_tournament_sse.py`** (NEW):
- `test_create_tournament_publishes_event`
- `test_update_tournament_publishes_event`
- `test_delete_tournament_publishes_event`

**`tests/test_game_sse.py`** (NEW):
- `test_create_game_publishes_event`
- `test_update_game_publishes_event`
- `test_delete_game_publishes_event`

### E2E tests

**`e2e/test_sse_realtime_e2e.py`** (NEW):
- `test_sse_dashboard_refreshes_on_rating_change`
- `test_sse_dashboard_refreshes_on_game_created`
- `test_sse_tournament_detail_refreshes_on_game_result`
- `test_sse_players_list_refreshes_on_rating_change`
- `test_sse_notification_toast_appears`
- `test_sse_reconnection_preserves_listeners`

### Verification
1. `cd backend && uv run pytest -v` — all tests pass
2. `cd backend && uv run ruff check` — no lint errors
3. E2E tests pass
4. Manual verification with 2 browser tabs

## [Documentation]

### PROMPTS.md
- Add record of this prompt

### CHANGES.md
- Add entry for all SSE changes

### REPORT.md
- "История работы" for each step
- "Ключевые проблемы и решения" for SSE format bug
- "Удачные/неудачные шаги"

### Memory Bank
- `activeContext.md`, `progress.md`, `js-sse.md`, `api-layer.md`

### Code review
- `code-reviewer` skill before commit

### Pre-commit checklist
1. All tests pass
2. Ruff clean
3. CHANGES.md, PROMPTS.md, REPORT.md updated
4. Memory Bank updated
5. Code review done
6. `git add -A && git commit` + `git push`

## [Implementation Order]

### Phase 1: TDD — Write tests first
1. Create `sse_events.py`
2. Create `tests/test_sse_events.py`
3. Create `tests/test_sse_service.py` (RED)
4. Create `tests/test_player_sse.py` (RED)
5. Create `tests/test_tournament_sse.py` (RED)
6. Create `tests/test_game_sse.py` (RED)

### Phase 2: Fix backend core (GREEN)
7. Fix `sse_service.py`
8. Verify test_sse_service passes

### Phase 3: Add SSE events to services
9. `player_service.py`
10. `tournament_service.py`
11. `game_service.py`
12. `import_service.py`
13. Run all unit tests

### Phase 4: Fix frontend
14. `sse.js`
15. `index.html`
16. `players/list.html`
17. `tournaments/detail.html`
18. `tournaments/list.html`

### Phase 5: E2E tests
19. `e2e/test_sse_realtime_e2e.py`
20. Update `e2e/test_m20_sse_realtime.py`
21. Run E2E tests

### Phase 6: Code review + docs + commit
22. Full test suite
23. Ruff check
24. Code review
25. Update PROMPTS.md, CHANGES.md, REPORT.md
26. Update Memory Bank
27. `git add -A && git commit` + `git push`