import asyncio
import hashlib
from dataclasses import asdict, dataclass


@dataclass
class AnnouncementItem:
    school: str
    title: str
    url: str
    date: str  # ISO yyyy-mm-dd
    body: str = ""

    def fingerprint(self) -> str:
        h = hashlib.sha256()
        h.update(self.title.encode())
        h.update(b"|")
        h.update(self.date.encode())
        h.update(b"|")
        h.update(self.body.encode())
        return h.hexdigest()

    def to_dict(self):
        return asdict(self)


class AsyncIteratorList(list):
    """Marker for fetchers that may grow to streaming in the future."""


class RateLimiter:
    """Per-adapter semaphore + global semaphore composition helper.

    Usage::

        async def fetch(self):
            async with self.rate_limit:
                return await self._do_fetch()
    """

    def __init__(self, inner: int = 2):
        self._inner = inner
        self._sem = asyncio.Semaphore(inner)

    @property
    def semaphore(self) -> asyncio.Semaphore:
        return self._sem

    async def __aenter__(self):
        await self._sem.acquire()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        try:
            self._sem.release()
        except ValueError:
            pass  # already released

    @property
    def in_flight(self) -> int:
        """How many slots are taken right now (for tests / metrics)."""
        # asyncio.Semaphore doesn't expose value publicly, but _value is accessible.
        # We avoid relying on private attrs in production; expose for tests.
        return self._inner - self._sem._value  # noqa: SLF001
