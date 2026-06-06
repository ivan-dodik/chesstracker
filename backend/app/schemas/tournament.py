"""Tournament schemas."""

from datetime import datetime

from pydantic import BaseModel


class TournamentCreate(BaseModel):
    """Schema for creating a new tournament."""
    name: str
    start_date: datetime
    end_date: datetime
    location: str | None = None
    rounds: int = 0
    type: str = "classic"
    status: str = "active"


class TournamentRead(BaseModel):
    """Schema for reading tournament details."""
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    location: str | None = None
    rounds: int
    type: str
    status: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class TournamentList(BaseModel):
    """Schema for listing tournaments (paginated)."""
    items: list[TournamentRead]
    total: int
    page: int
    per_page: int


class TournamentStandings(BaseModel):
    """Schema for tournament standings entry."""
    player_id: int
    player_name: str
    points: float
    games_played: int
