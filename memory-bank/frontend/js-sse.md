# SSE Client (`static/js/sse.js`)

## Overview
- **91 lines** — real-time event streaming via Server-Sent Events
- Auto-initializes on `DOMContentLoaded`

## SSEClient class

| Method | Purpose |
|--------|---------|
| `constructor()` | Starts connection with reconnect delay 3s |
| `connect()` | Creates `EventSource('/api/events')`, registers listeners |
| `showNotification(message, type)` | Delegates to `showFlash()` from main.js |
| `close()` | Closes EventSource |

## Event listeners

| Event | Trigger | Notification |
|-------|---------|-------------|
| `game_created` | New game added | `🎮 Новая партия: {white} vs {black} ({result})` |
| `game_result_updated` | Game result changed | `🔄 Результат обновлён: {white} vs {black} — {result}` |
| `rating_updated` | Rating changed | `📈 Рейтинг обновлён: {player} — {rating}` |
| `ping` | Keepalive (30s) | No action |

## Reconnect logic
- Initial delay: 3s
- Exponential backoff: `delay * 1.5` each retry
- Max delay: 30s
- Resets to 3s on successful connection

## Global
- `window.sseClient` — singleton instance, accessible from console

## Links
- → `frontend/js-main.md` — uses showFlash() from main.js
- → `backend/api-layer.md` — SSE endpoint `GET /api/events`
- → `backend/services-layer.md` — sse_service.py (pub/sub backend)