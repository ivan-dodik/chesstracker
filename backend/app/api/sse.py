"""SSE API — server-sent events endpoint."""

import asyncio

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from app.services.sse_service import subscribe, unsubscribe

router = APIRouter(prefix="/api", tags=["sse"])


@router.get("/events")
async def event_stream(request: Request) -> EventSourceResponse:
    """SSE endpoint for real-time events."""

    async def event_generator():
        queue = await subscribe("all")

        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    message = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield message
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": "keepalive"}

        finally:
            unsubscribe("all", queue)

    return EventSourceResponse(event_generator())