"""HTTP client for backend API."""

import logging

import httpx

from config import settings

logger = logging.getLogger(__name__)


class ApiClient:
    """Async HTTP client for the Chess Tracker backend."""

    def __init__(self) -> None:
        self.base_url = settings.BACKEND_URL.rstrip("/")
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)
        return self._client

    async def get_active_tournaments(self) -> list[dict]:
        """Return list of active tournaments."""
        client = await self._get_client()
        try:
            resp = await client.get("/api/tournaments", params={"status": "active", "per_page": 50})
            resp.raise_for_status()
            data = resp.json()
            return data.get("items", [])
        except httpx.HTTPError as exc:
            logger.error("Failed to fetch active tournaments: %s", exc)
            return []

    async def get_tournament_games(self, tournament_id: int, per_page: int = 100) -> list[dict]:
        """Return list of games for a given tournament."""
        client = await self._get_client()
        try:
            resp = await client.get(f"/api/tournaments/{tournament_id}/games", params={"per_page": per_page})
            resp.raise_for_status()
            data = resp.json()
            return data.get("items", [])
        except httpx.HTTPError as exc:
            logger.error("Failed to fetch games for tournament %s: %s", tournament_id, exc)
            return []

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
