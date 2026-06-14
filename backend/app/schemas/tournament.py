# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Tournament schemas."""

from datetime import datetime

from pydantic import BaseModel, field_validator

VALID_TOURNAMENT_TYPES = {"classic", "blitz", "rapid"}


class TournamentCreate(BaseModel):
    """Schema for creating a new tournament."""
    name: str
    start_date: datetime
    end_date: datetime
    location: str | None = None
    rounds: int = 0
    type: str = "classic"
    status: str = "active"

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in VALID_TOURNAMENT_TYPES:
            raise ValueError(f"Invalid tournament type: {v}. Must be one of: {', '.join(sorted(VALID_TOURNAMENT_TYPES))}")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v: datetime, info) -> datetime:
        if "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


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
    wins: int = 0
    draws: int = 0
    losses: int = 0
