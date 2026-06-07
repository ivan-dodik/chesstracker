"""Export API — CSV export endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models import User
from app.services.export_service import export_tournament_csv

router = APIRouter(prefix="/api/tournaments", tags=["export"])


@router.get("/{tournament_id}/export/csv", response_class=PlainTextResponse)
async def export_csv(
    tournament_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PlainTextResponse:
    """Export tournament standing as CSV."""
    csv_content = await export_tournament_csv(db, tournament_id)
    if csv_content is None:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return PlainTextResponse(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=tournament_{tournament_id}.csv"},
    )
