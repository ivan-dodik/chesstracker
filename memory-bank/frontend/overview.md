# Frontend Overview

## Architecture
- **No separate frontend server** — HTML rendered by FastAPI via Jinja2
- **HTMX 2.0.4** — dynamic content loading via `hx-*` attributes
- **Alpine.js 3.14.8** — client-side reactivity (auth state, forms, charts, detail pages)
- **Chart.js 4.4.7** — line chart (rating history) + doughnut chart (overall stats)
- **SSE** — real-time toast notifications via `EventSource`

## File structure
```
templates/
├── base.html              # Layout: nav, auth toggle, flash messages, footer
├── index.html             # Dashboard: top-10, favorites, active tournaments
├── login.html             # Login form (Alpine.js loginForm component)
├── players/
│   ├── list.html          # Search + filter + paginated table
│   └── detail.html        # Player profile: stats, chart, H2H, favorites
├── tournaments/
│   ├── list.html          # Filter by status/location + paginated table
│   └── detail.html        # Tournament info, standings, games table, chart
└── partials/
    ├── pagination.html    # HTMX-based pagination buttons
    ├── player_row.html    # Single player <tr>
    └── tournament_row.html # Single tournament <tr>

static/
├── css/style.css          # 681 lines: custom properties, responsive, components
└── js/
    ├── main.js            # 267 lines: Auth, HTMX config, Alpine components, utils
    └── sse.js             # 91 lines: SSEClient with reconnect
```

## Alpine.js components

| Component | File | Purpose |
|-----------|------|---------|
| `authState` | main.js | Login/logout toggle in navbar |
| `loginForm` | main.js | Login form submission |
| `pagination` | main.js | Pagination state management |
| `playerDetail` | detail.html | Player profile, chart, H2H, favorites |
| `tournamentDetail` | detail.html | Tournament info, standings, games |
| `ratingChart` | detail.html | Chart.js line chart wrapper |
| `overallStatsChart` | detail.html | Chart.js doughnut chart wrapper |
| `headToHead` | detail.html | Head-to-head stats selector |
| `accordion` | detail.html | Collapsible sections |

## Links
- → `frontend/templates.md` — all templates in detail
- → `frontend/css.md` — style.css breakdown
- → `frontend/js-main.md` — main.js (Auth, HTMX, Alpine)
- → `frontend/js-sse.md` — sse.js (SSE client)
- → `backend/web-layer.md` — web.py routes that render templates