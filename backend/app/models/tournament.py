# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Tournament model."""

import datetime

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Tournament(Base):
    __tablename__ = "tournaments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    start_date: Mapped[datetime.date] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime.date] = mapped_column(DateTime(timezone=True), nullable=False)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    rounds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    type: Mapped[str] = mapped_column(Enum("classic", "blitz", "rapid", name="tournament_type"), default="classic", nullable=False)
    status: Mapped[str] = mapped_column(Enum("active", "completed", name="tournament_status"), default="active", nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    games: Mapped[list["Game"]] = relationship("Game", back_populates="tournament", lazy="raise", cascade="all, delete-orphan")  # noqa: F821
    rating_history: Mapped[list["RatingHistory"]] = relationship(  # noqa: F821
        "RatingHistory", back_populates="tournament", lazy="raise"
    )
