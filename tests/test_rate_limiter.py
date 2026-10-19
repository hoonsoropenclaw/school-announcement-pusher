"""Tests for the per-adapter RateLimiter semaphore."""
from __future__ import annotations

import asyncio

import pytest

from fetcher.base import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_blocks_when_full():
    rl = RateLimiter(inner=1)
    async with rl:
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(rl.semaphore.acquire(), timeout=0.05)
    # After exit slot is free again.
    await asyncio.wait_for(rl.semaphore.acquire(), timeout=0.05)
    rl.semaphore.release()


@pytest.mark.asyncio
async def test_rate_limiter_exit_is_idempotent():
    rl = RateLimiter(inner=1)
    async with rl:
        pass
    # Double release must not raise; semaphore.release already swallows.
    rl.semaphore.release()
    # semaphore is now back at 1; we should be able to acquire twice sequentially.
    await rl.semaphore.acquire()
    await rl.semaphore.acquire()
    rl.semaphore.release()
    rl.semaphore.release()
