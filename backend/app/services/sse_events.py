# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""SSE event type constants."""


class SSEEvents:
    """Server-Sent Events type constants.

    All publish_event calls should use these constants as event_type
    to ensure consistent naming between backend and frontend listeners.
    """

    # Player events
    PLAYER_CREATED = "player_created"
    PLAYER_UPDATED = "player_updated"
    PLAYER_DELETED = "player_deleted"

    # Tournament events
    TOURNAMENT_CREATED = "tournament_created"
    TOURNAMENT_UPDATED = "tournament_updated"
    TOURNAMENT_DELETED = "tournament_deleted"

    # Game events
    GAME_CREATED = "game_created"
    GAME_UPDATED = "game_updated"
    GAME_DELETED = "game_deleted"

    # Rating events
    RATING_UPDATED = "rating_updated"
