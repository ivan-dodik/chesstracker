# Security Audit (`SECURITY_AUDIT.md`)

## Summary
| Severity | Count | Fixed |
|----------|-------|-------|
| Critical | 3 | 3 |
| Important | 3 | 3 |
| Minor | 3 | 0 (documented) |

## Critical fixes

| Issue | File | Fix |
|-------|------|-----|
| Default SECRET_KEY | `config.py` | Added `field_validator` with warning |
| N+1 queries in game_service | `game_service.py` | Replaced with `selectinload` |
| CSV import no size limit | `import_route.py` | Added 10 MB limit (HTTP 413) |

## Important fixes

| Issue | File | Fix |
|-------|------|-----|
| CORS `allow_origins=["*"]` | `main.py` | Documented for production |
| Duplicated standings logic | `tournament_service.py` + `export_service.py` | Created `standings_service.py` |
| Shared test.db file | `tests/conftest.py` | Uses `tempfile.mkstemp()` |

## Pending issues

| Issue | Recommendation |
|-------|---------------|
| SSE endpoint without auth | Add `Depends(get_current_user)` |
| ActivityLog JSON as strings | Use SQLAlchemy JSON type |
| No rate limiting on `/api/auth/login` | Add middleware (slowapi, nginx) |

## Architecture improvements (pending)
- **Shallow CRUD services**: Consider `BaseCRUDService` for player/favorite/rating
- **Rating engine coupled to DB**: Extract pure `calculate_elo_change()` function
- **Missing tests**: Import/Export/SSE/ActivityLog (now partially covered by M12)

## Links
- → `backend/core-layer.md` — config.py, security.py
- → `backend/services-layer.md` — standings_service, game_service
- → `testing/overview.md` — test coverage