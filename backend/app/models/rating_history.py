# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""RatingHistory model."""

import datetime

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RatingHistory(Base):
    __tablename__ = "rating_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    tournament_id: Mapped[int | None] = mapped_column(ForeignKey("tournaments.id", ondelete="SET NULL"), nullable=True)

    player: Mapped["Player"] = relationship("Player", back_populates="rating_history", lazy="selectin")  # noqa: F821
    tournament: Mapped["Tournament | None"] = relationship(  # noqa: F821
        "Tournament", back_populates="rating_history", lazy="selectin"
    )
