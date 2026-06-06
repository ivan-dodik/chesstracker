# Web Layer (`templates/` + `static/`)

## Frontend architecture
- **No separate frontend server** — HTML rendered by FastAPI via Jinja2
- **HTMX** — dynamic content loading via `hx-*` attributes (no custom JS for API calls)
- **Alpine.js** — client-side reactivity (auth state, forms, pagination)
- **Chart.js** — charts (planned for M7, not yet used)

## Templates (`templates/`)

### `base.html`
Base template with:
- Navigation bar (logo, Dashboard/Players/Tournaments links)
- Login/logout toggle via Alpine.js `authState()`
- Flash messages container (`#flash-messages`, JS-managed)
- Footer
- CDN: HTMX 2.0.4, Alpine.js 3.14.8, local main.js

### `index.html` (Dashboard)
- Top 10 players (HTMX → `GET /api/stats/top-rated`)
- Favorites section (HTMX → `GET /api/favorites`, shown only when authenticated)
- Active tournaments (HTMX → `GET /api/tournaments?status=active`)
- JSON response parsing in `htmx:afterSwap` handler
- Placeholder for recent results

### `login.html`
- Alpine.js `loginForm` component
- Form submits via `fetch()` → stores JWT in localStorage → redirects to `/`
- Demo credentials hint

### `players/list.html`
- Search by name (HTMX keyup delay:500ms)
- Filter by rating range, city
- Paginated table via `fetch()` + manual `renderPlayersTable()`
- Shows "Add player" button for admins only

### `tournaments/list.html`
- Filter by status (dropdown) + location
- Paginated table
- Shows "Create tournament" button for admins only

### Partials (`partials/`)
- `player_row.html` — single player `<tr>`
- `tournament_row.html` — single tournament `<tr>`
- `pagination.html` — HTMX-based pagination buttons

## Static files (`static/`)

### `css/style.css` (681 lines)
- CSS custom properties for theming
- Responsive (mobile ≤576px, tablet ≤768px, desktop)
- Components: navbar, cards, tables, buttons, forms, badges, flash messages, pagination, dashboard grid, empty state, spinner, toast

### `js/main.js` (267 lines)
- `Auth` object: getToken/setToken/clearToken/isAuthenticated/getUser/isAdmin/getAuthHeaders/logout
- HTMX config: auto-adds `Authorization: Bearer` header, handles 401 errors
- Alpine.js components: `authState`, `loginForm`, `pagination`
- Utilities: `showFlash()`, `formatDate()`, `formatRating()`

## Web routes (`api/web.py`)
- Custom Jinja2 `Environment` with `cache_size=0` (workaround for Jinja2 3.1.x incompatibility with Starlette Jinja2Templates)
- `TemplateResponse()` helper function
- Routes: `GET /`, `/login`, `/players`, `/tournaments`

## Known issues
- **Jinja2 cache error** resolved via cache_size=0
- **get_flashed_messages** removed (Flask-specific, managed via JS now)

## Links
- → `modules/api-layer.md` (web.py routes, API endpoints called by HTMX)
- → `modules/docker-infra.md` (static files served via FastAPI)