"""School A: Jinja-rendered list page, needs Playwright."""
from __future__ import annotations

from .base import AnnouncementItem, RateLimiter


class SchoolAAdapter:
    name = "school_a"

    def __init__(self, inner_concurrency: int = 1):
        self.rate_limit = RateLimiter(inner=inner_concurrency)

    async def __aenter__(self):
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            self._client = None
            return self
        self._client = await async_playwright().start()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._client:
            await self._client.stop()

    async def fetch(self) -> list[AnnouncementItem]:
        if self._client is None:
            return _demo_items("school_a")
        # Adapter-internal concurrency cap protects a single school from
        # hammering Playwright even if outer semaphore is loose.
        async with self.rate_limit:
            browser = await self._client.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                await page.goto("https://example.edu/announcements", timeout=15000)
                rows = await page.locator("li.announcement").all()
                out = []
                for row in rows:
                    title = (await row.locator("h4").inner_text()).strip()
                    url = await row.locator("a").get_attribute("href")
                    date = (await row.locator("time").inner_text()).strip()
                    out.append(AnnouncementItem("school_a", title, url, date))
                return out
            finally:
                await browser.close()

def _demo_items(school: str):
    from datetime import date
    return [
        AnnouncementItem(school, "Demo: 校慶延期通知", f"https://example.edu/{school}/1", date.today().isoformat(), "因天候延期"),
    ]
