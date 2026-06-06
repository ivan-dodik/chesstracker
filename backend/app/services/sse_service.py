"""SSE service — server-sent events for real-time updates."""

import asyncio
import json
from datetime import UTC, datetime
from typing import Any

event_subscribers: dict[str, list[asyncio.Queue]] = {}


async def subscribe(event_type: str) -> asyncio.Queue:
    """Subscribe to an event type. Returns a queue for receiving events."""
    queue: asyncio.Queue = asyncio.Queue()
    if event_type not in event_subscribers:
        event_subscribers[event_type] = []
    event_subscribers[event_type].append(queue)
    return queue


def unsubscribe(event_type: str, queue: asyncio.Queue) -> None:
    """Unsubscribe a queue from an event type."""
    if event_type in event_subscribers:
        event_subscribers[event_type] = [
            q for q in event_subscribers[event_type] if q is not queue
        ]
        if not event_subscribers[event_type]:
            del event_subscribers[event_type]


async def publish_event(event_type: str, data: dict[str, Any]) -> None:
    """Publish an event to all subscribers of the given type."""
    event_data = {
        "type": event_type,
        "data": data,
        "timestamp": datetime.now(UTC).isoformat(),
    }

    message = f"data: {json.dumps(event_data, default=str)}\n\n"

    # Publish to specific event type subscribers
    if event_type in event_subscribers:
        for queue in event_subscribers[event_type]:
            await queue.put(message)

    # Also publish to "all" subscribers
    if "all" in event_subscribers:
        for queue in event_subscribers["all"]:
            await queue.put(message)
