# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Player schemas."""

from datetime import datetime

from pydantic import BaseModel, field_validator


class PlayerCreate(BaseModel):
    """Schema for creating a new player."""
    name: str
    rating: int = 0
    city: str | None = None
    avatar_url: str | None = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Rating cannot be negative")
        return v


class PlayerUpdate(BaseModel):
    """Schema for updating player data."""
    name: str | None = None
    rating: int | None = None
    city: str | None = None
    avatar_url: str | None = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("Rating cannot be negative")
        return v


class PlayerRead(BaseModel):
    """Schema for reading player details."""
    id: int
    name: str
    rating: int
    city: str | None = None
    avatar_url: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class PlayerList(BaseModel):
    """Schema for listing players (paginated)."""
    items: list[PlayerRead]
    total: int
    page: int
    per_page: int
