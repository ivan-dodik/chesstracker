# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Tests for SSE service — publish_event, subscribe, unsubscribe."""

import asyncio
import json

import pytest

from app.services.sse_service import event_subscribers, publish_event, subscribe, unsubscribe


@pytest.fixture(autouse=True)
def clean_subscribers():
    """Ensure event_subscribers is clean before and after each test."""
    event_subscribers.clear()
    yield
    event_subscribers.clear()


@pytest.mark.asyncio
async def test_subscribe_returns_queue():
    """subscribe() must return an asyncio.Queue."""
    queue = await subscribe("all")
    assert isinstance(queue, asyncio.Queue)
    # Cleanup
    unsubscribe("all", queue)


@pytest.mark.asyncio
async def test_subscribe_registers_queue():
    """subscribe() must register the queue in event_subscribers."""
    queue = await subscribe("rating_updated")
    assert "rating_updated" in event_subscribers
    assert queue in event_subscribers["rating_updated"]
    unsubscribe("rating_updated", queue)


@pytest.mark.asyncio
async def test_unsubscribe_removes_queue():
    """unsubscribe() must remove the queue from event_subscribers."""
    queue = await subscribe("all")
    assert queue in event_subscribers["all"]
    unsubscribe("all", queue)
    assert queue not in event_subscribers.get("all", [])


@pytest.mark.asyncio
async def test_unsubscribe_deletes_empty_type():
    """unsubscribe() must delete the event type key when no subscribers remain."""
    queue = await subscribe("game_created")
    unsubscribe("game_created", queue)
    assert "game_created" not in event_subscribers


@pytest.mark.asyncio
async def test_publish_event_returns_dict():
    """publish_event must put a dict (not a string) into subscriber queues.

    The dict must have 'event' and 'data' keys for sse-starlette to correctly
    format the SSE message with event type and data fields.
    """
    queue = await subscribe("all")
    await publish_event("rating_updated", {"player_id": 1, "new_rating": 1500})

    message = await queue.get()
    assert isinstance(message, dict)
    assert "event" in message
    assert "data" in message
    unsubscribe("all", queue)


@pytest.mark.asyncio
async def test_publish_event_sets_event_type():
    """The 'event' field must match the event_type parameter."""
    queue = await subscribe("all")
    await publish_event("game_created", {"game_id": 42})

    message = await queue.get()
    assert message["event"] == "game_created"
    unsubscribe("all", queue)


@pytest.mark.asyncio
async def test_publish_event_data_is_json_string():
    """The 'data' field must be a JSON-encoded string."""
    queue = await subscribe("all")
    payload = {"player_id": 1, "player_name": "Test", "rating": 1500}
    await publish_event("rating_updated", payload)

    message = await queue.get()
    assert isinstance(message["data"], str)
    parsed = json.loads(message["data"])
    assert parsed["data"] == payload
    unsubscribe("all", queue)


@pytest.mark.asyncio
async def test_publish_to_specific_subscribers():
    """publish_event must send to subscribers of the specific event type."""
    queue = await subscribe("rating_updated")
    await publish_event("rating_updated", {"player_id": 1})

    assert not queue.empty()
    message = await queue.get()
    assert message["event"] == "rating_updated"
    unsubscribe("rating_updated", queue)


@pytest.mark.asyncio
async def test_publish_to_all_subscribers():
    """publish_event must also send to subscribers of 'all' event type."""
    queue = await subscribe("all")
    await publish_event("rating_updated", {"player_id": 1})

    assert not queue.empty()
    message = await queue.get()
    assert message["event"] == "rating_updated"
    unsubscribe("all", queue)


@pytest.mark.asyncio
async def test_publish_does_not_cross_types():
    """publish_event must not send to unrelated event type subscribers."""
    queue_game = await subscribe("game_created")
    await publish_event("rating_updated", {"player_id": 1})

    # game_created queue should NOT receive rating_updated events
    assert queue_game.empty()
    unsubscribe("game_created", queue_game)


@pytest.mark.asyncio
async def test_unsubscribe_does_not_affect_other_queues():
    """unsubscribe must only remove the specified queue."""
    queue1 = await subscribe("all")
    queue2 = await subscribe("all")
    unsubscribe("all", queue1)
    assert queue2 in event_subscribers["all"]
    unsubscribe("all", queue2)
