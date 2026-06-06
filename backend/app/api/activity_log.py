"""ActivityLog API — activity log endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_db
from app.models import User
from app.services.activity_log_service import get_activity_log

router = APIRouter(prefix="/api/activity-log", tags=["activity-log"])


@router.get("")
async def read_activity_log(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    entity_type: str | None = Query(None),
    action: str | None = Query(None),
    user_id: int | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get paginated activity log (admin only)."""
    logs, total = await get_activity_log(
        db=db,
        page=page,
        per_page=per_page,
        entity_type=entity_type,
        action=action,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
    )
    return {
        "items": logs,
        "total": total,
        "page": page,
        "per_page": per_page,
    }