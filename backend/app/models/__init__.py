"""SQLAlchemy models package."""

from app.core.database import Base
from app.models.activity_log import ActivityLog  # noqa: F401, E402
from app.models.favorite import Favorite  # noqa: F401, E402
from app.models.game import Game  # noqa: F401, E402
from app.models.player import Player  # noqa: F401, E402
from app.models.rating_history import RatingHistory  # noqa: F401, E402
from app.models.tournament import Tournament  # noqa: F401, E402

# Import models so they are registered with SQLAlchemy metadata
from app.models.user import User  # noqa: F401, E402

__all__ = [
    "Base",
    "User",
    "Player",
    "Tournament",
    "Game",
    "RatingHistory",
    "Favorite",
    "ActivityLog",
]
