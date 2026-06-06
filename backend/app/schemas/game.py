"""Game schemas."""

from datetime import datetime

from pydantic import BaseModel


class GameCreate(BaseModel):
    """Schema for creating a new game."""
    tournament_id: int
    round: int
    white_player_id: int
    black_player_id: int
    result: str | None = None
    played_at: datetime | None = None


class GameRead(BaseModel):
    """Schema for reading game details."""
    id: int
    tournament_id: int
    round: int
    white_player_id: int
    black_player_id: int
    result: str | None = None
    played_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class GameResult(BaseModel):
    """Schema for updating game result."""
    result: str
