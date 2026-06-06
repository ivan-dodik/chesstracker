"""Import API — CSV import endpoints."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_db
from app.models import User
from app.services.import_service import import_tournament_csv

router = APIRouter(prefix="/api/tournaments", tags=["import"])


MAX_CSV_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/{tournament_id}/import/csv")
async def import_csv(
    tournament_id: int,
    file: UploadFile,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Import tournament results from CSV file."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported",
        )

    # Read file with size limit to prevent DoS
    raw_data = await file.read()
    if len(raw_data) > MAX_CSV_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {MAX_CSV_SIZE // (1024 * 1024)} MB",
        )
    content = raw_data.decode("utf-8")
    result = await import_tournament_csv(db, tournament_id, content)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Import failed"),
        )

    return result
