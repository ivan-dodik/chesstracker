"""ActivityLog schemas."""

from datetime import datetime

from pydantic import BaseModel


class ActivityLogRead(BaseModel):
    """Schema for reading activity log entry."""
    id: int
    user_id: int | None = None
    action: str
    entity_type: str
    entity_id: int | None = None
    old_values: dict | None = None
    new_values: dict | None = None
    timestamp: datetime

    model_config = {"from_attributes": True}
