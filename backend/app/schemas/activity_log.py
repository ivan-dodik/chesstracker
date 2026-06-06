"""ActivityLog schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ActivityLogRead(BaseModel):
    """Schema for reading activity log entry."""
    id: int
    user_id: Optional[int] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    old_values: Optional[dict] = None
    new_values: Optional[dict] = None
    timestamp: datetime

    model_config = {"from_attributes": True}