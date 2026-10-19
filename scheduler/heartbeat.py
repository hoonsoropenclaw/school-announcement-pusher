"""Heartbeat: ping monitoring URL after success / fail."""
import logging
import urllib.request

log = logging.getLogger("heartbeat")

class Heartbeat:
    def __init__(self, url: str | None):
        self.url = url

    def ping(self, suffix: str = "") -> None:
        if not self.url:
            return
        try:
            target = self.url + ("/" + suffix if suffix else "")
            urllib.request.urlopen(target, timeout=5).read()
        except Exception:
            log.warning("heartbeat failed", exc_info=True)

    fail = ping  # same shape, alias for clarity
