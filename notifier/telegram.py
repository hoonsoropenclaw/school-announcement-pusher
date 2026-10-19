"""Telegram notifier with dry-run fallback."""
import logging

import httpx
from tenacity import retry, stop_after_attempt, wait_random_exponential

log = logging.getLogger("telegram")

class TelegramNotifier:
    def __init__(self, token: str, chat_id: str, dry_run: bool = False):
        self.token = token
        self.chat_id = chat_id
        self.dry_run = dry_run or not token

    @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(1, 30))
    async def send(self, item) -> None:
        text = (
            f"[{item.school}] {item.title}\n"
            f"{item.date}\n{item.url}"
        )
        if self.dry_run:
            log.info("[DRY-RUN] %s", text)
            return
        async with httpx.AsyncClient(timeout=10) as cx:
            r = await cx.post(
                f"https://api.telegram.org/bot{self.token}/sendMessage",
                json={"chat_id": self.chat_id, "text": text},
            )
            r.raise_for_status()
