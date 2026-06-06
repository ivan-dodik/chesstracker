# main.js (`static/js/main.js`)

## Overview
- **267 lines** — core JavaScript for the frontend
- Handles: authentication, HTMX integration, Alpine.js components, utilities

## Auth object

| Method | Purpose |
|--------|---------|
| `getToken()` | Returns JWT from localStorage |
| `setToken(token)` | Stores JWT in localStorage |
| `clearToken()` | Removes JWT from localStorage |
| `isAuthenticated()` | Boolean — token exists |
| `getUser()` | Decoded JWT payload (sub, role, exp) |
| `isAdmin()` | Boolean — role === "admin" |
| `getAuthHeaders()` | `{"Authorization": "Bearer <token>"}` |
| `logout()` | Clears token, redirects to `/login` |

## HTMX integration

| Config | Detail |
|--------|--------|
| `htmx:configRequest` | Auto-adds `Authorization: Bearer` header to all HTMX requests |
| `htmx:afterOnLoad` | Handles 401 responses → redirects to `/login` |
| `htmx:afterSwap` | Parses JSON responses for dashboard sections |

## Alpine.js components

### `authState`
- `isAuthenticated` — bound to Auth.isAuthenticated()
- `isAdmin` — bound to Auth.isAdmin()
- `logout()` — calls Auth.logout()

### `loginForm`
- `username`, `password` — form fields
- `error` — error message string
- `loading` — boolean for submit state
- `submit()` — POST `/api/auth/login`, stores token, redirects to `/`

### `pagination`
- `page`, `perPage`, `total` — state
- `totalPages()` — computed from total/perPage
- `pages()` — array of page numbers for rendering
- `goToPage(p)` — updates page, triggers data reload

## Utility functions

| Function | Purpose |
|----------|---------|
| `showFlash(message, type)` | Creates flash message toast (auto-dismiss 5s) |
| `formatDate(dateStr)` | Formats ISO date to `DD.MM.YYYY` |
| `formatRating(rating)` | Formats rating number |

## Links
- → `frontend/overview.md` — architecture
- → `frontend/js-sse.md` — SSE client
- → `frontend/templates.md` — templates that use these components