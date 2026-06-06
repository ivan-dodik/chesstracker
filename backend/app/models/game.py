"""Game model."""

import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False, index=True)
    round: Mapped[int] = mapped_column(Integer, nullable=False)
    white_player_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    black_player_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    result: Mapped[str | None] = mapped_column(Enum("1-0", "0-1", "½-½", name="game_result"), nullable=True)
    played_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tournament: Mapped["Tournament"] = relationship("Tournament", back_populates="games", lazy="selectin")  # noqa: F821
    white_player: Mapped["Player"] = relationship("Player", foreign_keys=[white_player_id], back_populates="games_as_white", lazy="selectin")  # noqa: F821
    black_player: Mapped["Player"] = relationship("Player", foreign_keys=[black_player_id], back_populates="games_as_black", lazy="selectin")  # noqa: F821
