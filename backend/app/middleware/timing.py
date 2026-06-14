# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Request timing middleware — logs every HTTP request with processing time."""

import logging
import time

logger = logging.getLogger("chesstracker.timing")


class TimingMiddleware:
    """ASGI middleware that logs method, path, status, and elapsed time.

    Also adds ``X-Process-Time`` response header for client-side diagnostics.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        start = time.perf_counter()
        path = scope.get("path", "")
        method = scope.get("method", "")
        client = scope.get("client", ("?", "?"))
        client_str = f"{client[0]}:{client[1]}" if client else "?"

        logger.info(">>> %s %s [%s] — started", method, path, client_str)

        status_code = None
        headers_sent = False

        async def send_wrapper(message):
            nonlocal status_code, headers_sent
            if message["type"] == "http.response.start":
                status_code = message.get("status", 0)
                # Inject X-Process-Time header
                elapsed = time.perf_counter() - start
                existing = list(message.get("headers", []))
                existing.append((b"x-process-time", f"{elapsed:.4f}".encode()))
                message["headers"] = existing
                headers_sent = True
            return await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            elapsed = time.perf_counter() - start
            logger.exception(
                "!!! %s %s [%s] — ERROR after %.3fs", method, path, client_str, elapsed,
            )
            raise

        elapsed = time.perf_counter() - start
        logger.info(
            "<<< %s %s [%s] — %s — %.4fs",
            method, path, client_str, status_code, elapsed,
        )
