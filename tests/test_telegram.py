import asyncio
import logging

from fetcher.base import AnnouncementItem
from notifier.telegram import TelegramNotifier


def test_dry_run(caplog):
    async def go():
        n = TelegramNotifier(token="", chat_id="", dry_run=True)
        with caplog.at_level(logging.INFO):
            await n.send(AnnouncementItem("school_a", "T", "u", "2026-10-18", "B"))
    asyncio.run(go())
    assert any("DRY-RUN" in r.message for r in caplog.records)
