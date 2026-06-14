# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Player model."""

import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    rating: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    games_as_white: Mapped[list["Game"]] = relationship("Game", foreign_keys="Game.white_player_id", back_populates="white_player", lazy="raise")  # noqa: F821
    games_as_black: Mapped[list["Game"]] = relationship("Game", foreign_keys="Game.black_player_id", back_populates="black_player", lazy="raise")  # noqa: F821
    rating_history: Mapped[list["RatingHistory"]] = relationship("RatingHistory", back_populates="player", lazy="raise")  # noqa: F821
    favorites: Mapped[list["Favorite"]] = relationship("Favorite", back_populates="player", lazy="raise")  # noqa: F821
