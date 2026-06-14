# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Favorite schemas."""

from datetime import datetime

from pydantic import BaseModel


class FavoritePlayerInfo(BaseModel):
    """Nested player info for favorite response."""
    id: int
    name: str
    rating: int | None = None
    city: str | None = None

    model_config = {"from_attributes": True}


class FavoriteRead(BaseModel):
    """Schema for reading favorite entry."""
    id: int
    user_id: int
    player_id: int
    created_at: datetime
    player: FavoritePlayerInfo | None = None

    model_config = {"from_attributes": True}
