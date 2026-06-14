# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Game schemas."""

from datetime import datetime

from pydantic import BaseModel, field_validator

VALID_GAME_RESULTS = {"1-0", "0-1", "½-½"}


class GameCreate(BaseModel):
    """Schema for creating a new game."""
    tournament_id: int | None = None
    game_round: int
    white_player_id: int
    black_player_id: int
    result: str | None = None
    played_at: datetime | None = None

    @field_validator("result")
    @classmethod
    def validate_result(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_GAME_RESULTS:
            raise ValueError(f"Invalid game result: {v}. Must be one of: {', '.join(sorted(VALID_GAME_RESULTS))}")
        return v


class GameRead(BaseModel):
    """Schema for reading game details."""
    id: int
    tournament_id: int
    tournament_name: str | None = None
    game_round: int
    white_player_id: int
    black_player_id: int
    white_player_name: str | None = None
    black_player_name: str | None = None
    result: str | None = None
    played_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class GameList(BaseModel):
    """Schema for listing games (paginated)."""
    items: list[GameRead]
    total: int
    page: int
    per_page: int


class GameUpdate(BaseModel):
    """Schema for updating game data."""
    game_round: int | None = None
    white_player_id: int | None = None
    black_player_id: int | None = None
    result: str | None = None
    played_at: datetime | None = None

    @field_validator("result")
    @classmethod
    def validate_result(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_GAME_RESULTS:
            raise ValueError(f"Invalid game result: {v}. Must be one of: {', '.join(sorted(VALID_GAME_RESULTS))}")
        return v


class GameResult(BaseModel):
    """Schema for updating game result."""
    result: str

    @field_validator("result")
    @classmethod
    def validate_result(cls, v: str) -> str:
        if v not in VALID_GAME_RESULTS:
            raise ValueError(f"Invalid game result: {v}. Must be one of: {', '.join(sorted(VALID_GAME_RESULTS))}")
        return v
