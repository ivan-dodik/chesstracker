# Templates (`templates/`)

## `base.html`
- Navigation bar: logo, Dashboard/Players/Tournaments links
- Auth toggle via Alpine.js `authState()` — shows login/logout
- Flash messages container (`#flash-messages`, JS-managed)
- Footer with copyright
- CDN imports: HTMX 2.0.4, Alpine.js 3.14.8, Chart.js 4.4.7, local main.js + sse.js

## `index.html` (Dashboard)
- Top 10 players (HTMX → `GET /api/stats/top-rated`)
- Favorites section (HTMX → `GET /api/favorites`, shown only when authenticated)
- Active tournaments (HTMX → `GET /api/tournaments?status=active`)
- JSON response parsing in `htmx:afterSwap` handler
- Placeholder for recent results

## `login.html`
- Alpine.js `loginForm` component
- Form submits via `fetch()` → stores JWT in localStorage → redirects to `/`
- Demo credentials hint: admin/admin123, user/user123

## `players/list.html`
- Search by name (HTMX keyup delay:500ms)
- Filter by rating range (min/max), city
- Paginated table via `fetch()` + manual `renderPlayersTable()`
- "Add player" button visible only for admins

## `players/detail.html` (245 lines)
- Alpine.js `playerDetail` component with methods:
  - `init()` — loads player, stats, players list, renders chart
  - `loadPlayer()` → `GET /api/players/{id}`
  - `loadOverallStats()` → `GET /api/stats/overall/{id}`
  - `loadPlayersList()` → `GET /api/players?per_page=200`
  - `renderRatingChart()` — Chart.js line chart from rating history
  - `loadHeadToHead()` → `GET /api/stats/head-to-head/{p1}/{p2}`
  - `toggleFavorite()` → POST/DELETE `/api/favorites/{id}`
- Sections: player header, stats grid (wins/losses/draws/win%), rating chart, head-to-head selector, tournaments list

## `tournaments/list.html`
- Filter by status (dropdown: all/active/completed) + location text input
- Paginated table
- "Create tournament" button visible only for admins

## `tournaments/detail.html`
- Alpine.js `tournamentDetail` component
- Tournament info header (name, dates, location, type, status)
- Standings table (HTMX → `GET /api/tournaments/{id}/standings`)
- Games table (HTMX → `GET /api/tournaments/{id}/games`)
- Chart.js doughnut chart for result distribution
- Export CSV button → `GET /api/tournaments/{id}/export/csv`
- Import CSV form (admin only) → POST multipart upload

## Partials (`partials/`)
- `player_row.html` — single `<tr>` with player data
- `tournament_row.html` — single `<tr>` with tournament data
- `pagination.html` — HTMX-based pagination buttons with `hx-get`, `hx-target`, `hx-swap`

## Links
- → `frontend/overview.md` — architecture overview
- → `backend/web-layer.md` — web.py routes
- → `backend/api-layer.md` — API endpoints called by HTMX