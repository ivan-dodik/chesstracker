"""Player schemas."""

from datetime import datetime

from pydantic import BaseModel


class PlayerCreate(BaseModel):
    """Schema for creating a new player."""
    name: str
    rating: int = 0
    city: str | None = None
    avatar_url: str | None = None


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
