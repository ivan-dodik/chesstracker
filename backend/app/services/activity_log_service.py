"""ActivityLog service — logging and reading activity log entries."""

import json
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ActivityLog


async def log_activity(
    db: AsyncSession,
    user_id: int | None,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    old_values: dict[str, Any] | None = None,
    new_values: dict[str, Any] | None = None,
) -> ActivityLog:
    """Create a new activity log entry."""
    log_entry = ActivityLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_values=json.dumps(old_values) if old_values else None,
        new_values=json.dumps(new_values) if new_values else None,
    )
    db.add(log_entry)
    await db.flush()
    await db.refresh(log_entry)
    return log_entry


async def get_activity_log(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 50,
    entity_type: str | None = None,
    action: str | None = None,
    user_id: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """Get paginated activity log with optional filters."""
    query = select(ActivityLog)
    count_query = select(func.count(ActivityLog.id))

    if entity_type:
        query = query.where(ActivityLog.entity_type == entity_type)
        count_query = count_query.where(ActivityLog.entity_type == entity_type)
    if action:
        query = query.where(ActivityLog.action == action)
        count_query = count_query.where(ActivityLog.action == action)
    if user_id is not None:
        query = query.where(ActivityLog.user_id == user_id)
        count_query = count_query.where(ActivityLog.user_id == user_id)
    if date_from:
        query = query.where(ActivityLog.timestamp >= date_from)
        count_query = count_query.where(ActivityLog.timestamp >= date_from)
    if date_to:
        query = query.where(ActivityLog.timestamp <= date_to)
        count_query = count_query.where(ActivityLog.timestamp <= date_to)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(ActivityLog.timestamp.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    logs = list(result.scalars().all())

    # Convert to dict with deserialized values
    result_list: list[dict[str, Any]] = []
    for log in logs:
        log_dict = {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "old_values": json.loads(log.old_values) if log.old_values else None,
            "new_values": json.loads(log.new_values) if log.new_values else None,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
        }
        result_list.append(log_dict)

    return result_list, total
