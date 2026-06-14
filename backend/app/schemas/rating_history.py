# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

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
