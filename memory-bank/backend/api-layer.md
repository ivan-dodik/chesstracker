# API Layer (`app/api/`)

## 12 route modules + 1 router + 1 deps

### Router (`router.py`)
Combines all sub-routers into `api_router`. Included routers: activity_log, auth, export, favorites, games, import, players, ratings, sse, stats, tournaments.

### Dependencies (`deps.py`)
| Dependency | Type | Notes |
|------------|------|-------|
| `get_db()` | `AsyncSession` | Per-request session |
| `get_current_user()` | `User` | JWT from `Authorization: Bearer` |
| `get_current_admin()` | `User` | Calls get_current_user + checks role |

### Endpoints

#### Auth (`auth.py` — prefix `/api/auth`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/login` | None | Returns JWT |
| POST | `/register` | Admin | Create new user |
| GET | `/me` | Any | Current user info |

#### Players (`players.py` — prefix `/api/players`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | Any | List (page, per_page, name, rating_min, rating_max, city) |
| POST | `/` | Admin | Create |
| GET | `/{id}` | Any | Details |
| PUT | `/{id}` | Admin | Update |
| DELETE | `/{id}` | Admin | Delete |

#### Tournaments (`tournaments.py` — prefix `/api/tournaments`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | Any | List (page, per_page, status, location) |
| POST | `/` | Admin | Create |
| GET | `/{id}` | Any | Details |
| PUT | `/{id}` | Admin | Update |
| DELETE | `/{id}` | Admin | Delete |
| GET | `/{id}/standings` | Any | Tournament table |

#### Games (`games.py` — no prefix, full paths)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/tournaments/{id}/games` | Any | List (page, per_page) |
| POST | `/api/tournaments/{id}/games` | Admin | Create |
| PUT | `/api/games/{id}` | Admin | Update result |
| DELETE | `/api/games/{id}` | Admin | Delete |

#### Ratings (`ratings.py` — prefix `/api/players`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/{id}/rating-history` | Any | date_from, date_to filters |

#### Stats (`stats.py` — prefix `/api/stats`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/head-to-head/{p1}/{p2}` | Any | H2H stats |
| GET | `/top-rated` | Any | limit param (default 10) |
| GET | `/overall/{player_id}` | Any | Wins/losses/draws |

#### Favorites (`favorites.py` — prefix `/api/favorites`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | Any (auth) | User's favorites |
| POST | `/{player_id}` | Any (auth) | Add favorite |
| DELETE | `/{player_id}` | Any (auth) | Remove favorite |

#### Activity Log (`activity_log.py` — prefix `/api/activity-log`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | Admin | Paginated log with filters |

#### Export (`export.py` — prefix `/api/tournaments`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/{id}/export/csv` | Any | CSV download |

#### Import (`import_route.py` — prefix `/api/tournaments`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/{id}/import/csv` | Admin | CSV upload (multipart) |

#### SSE (`sse.py` — prefix `/api`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/events` | Any | SSE event stream |

#### Web Routes (`web.py` — no prefix)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Dashboard (index.html) |
| GET | `/login` | Login page |
| GET | `/players` | Players list |
| GET | `/tournaments` | Tournaments list |

## FastAPI app (main.py)
- CORS: all origins allowed
- Static files mounted at `/static`
- `GET /health` → `{"status": "ok"}`

## Links
- → `modules/services-layer.md` (API calls services)
- → `modules/schemas-layer.md` (API uses schemas for validation/serialization)
- → `modules/core-layer.md` (deps imports from core)
- → `modules/web-layer.md` (templates rendered by web.py)