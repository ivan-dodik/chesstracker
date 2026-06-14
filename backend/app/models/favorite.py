# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Favorite model."""

import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="favorites", lazy="selectin")  # noqa: F821
    player: Mapped["Player"] = relationship("Player", back_populates="favorites", lazy="selectin")  # noqa: F821

    __table_args__ = (UniqueConstraint("user_id", "player_id", name="uq_user_player_favorite"),)
