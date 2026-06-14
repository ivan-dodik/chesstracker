# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""ActivityLog model."""

import datetime
import json

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    old_values: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_values: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="activity_logs", lazy="selectin")  # noqa: F821

    def set_old_values(self, data: dict | None) -> None:
        """Serialize dict to JSON string for storage."""
        self.old_values = json.dumps(data) if data else None

    def get_old_values(self) -> dict | None:
        """Deserialize JSON string back to dict."""
        return json.loads(self.old_values) if self.old_values else None

    def set_new_values(self, data: dict | None) -> None:
        """Serialize dict to JSON string for storage."""
        self.new_values = json.dumps(data) if data else None

    def get_new_values(self) -> dict | None:
        """Deserialize JSON string back to dict."""
        return json.loads(self.new_values) if self.new_values else None
