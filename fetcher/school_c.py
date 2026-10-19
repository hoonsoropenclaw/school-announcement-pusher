"""School C: RSS feed via feedparser."""
from __future__ import annotations

from .base import AnnouncementItem, RateLimiter


class SchoolCAdapter:
    name = "school_c"

    def __init__(self, inner_concurrency: int = 1):
        # RSS fetch is usually cheap; cap to 1 to avoid refresh storms.
        self.rate_limit = RateLimiter(inner=inner_concurrency)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def fetch(self) -> list[AnnouncementItem]:
        async with self.rate_limit:
            try:
                import feedparser
            except ImportError:
                return [AnnouncementItem("school_c", "Demo: 親師座談", "https://example.edu/school_c/1", "2026-10-12", "")]
            feed = feedparser.parse("https://example.edu/rss.xml")
            return [
                AnnouncementItem(
                    "school_c",
                    e.title,
                    e.link,
                    e.get("published", "")[:10],
                    e.get("summary", ""),
                )
                for e in feed.entries[:30]
            ]
