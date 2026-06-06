"""User model."""

import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(Enum("admin", "user", name="user_role"), default="user", nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    favorites: Mapped[list["Favorite"]] = relationship("Favorite", back_populates="user", lazy="selectin")  # noqa: F821
    activity_logs: Mapped[list["ActivityLog"]] = relationship("ActivityLog", back_populates="user", lazy="selectin")  # noqa: F821
