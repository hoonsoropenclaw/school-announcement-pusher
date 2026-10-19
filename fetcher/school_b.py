"""School B: JSON API."""
from __future__ import annotations

import httpx
from tenacity import retry, stop_after_attempt, wait_random_exponential

from .base import AnnouncementItem, RateLimiter


class SchoolBAdapter:
    name = "school_b"

    def __init__(self, inner_concurrency: int = 2):
        self.rate_limit = RateLimiter(inner=inner_concurrency)

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=10)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._client.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(1, 30))
    async def fetch(self) -> list[AnnouncementItem]:
        # Outer semaphore caps global fan-out; inner semaphore caps
        # this adapter's simultaneous GETs (avoid DOS-ing school's API).
        async with self.rate_limit:
            try:
                r = await self._client.get("https://example.edu/api/announcements")
                r.raise_for_status()
                data = r.json()
            except Exception:
                return [AnnouncementItem("school_b", "Demo: 圖書館週", "https://example.edu/school_b/1", "2026-10-15", "")]
            return [
                AnnouncementItem("school_b", i["title"], i["url"], i["date"], i.get("body", ""))
                for i in data.get("items", [])
            ]
