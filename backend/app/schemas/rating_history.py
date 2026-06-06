"""RatingHistory schemas."""

from datetime import datetime

from pydantic import BaseModel


class RatingHistoryRead(BaseModel):
    """Schema for reading rating history entry."""
    id: int
    player_id: int
    rating: int
    date: datetime
    tournament_id: int | None = None

    model_config = {"from_attributes": True}
