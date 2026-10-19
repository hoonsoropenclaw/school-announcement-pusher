#!/usr/bin/env python3
"""Daily school announcement crawler + dedup + Telegram push."""
import argparse, asyncio, logging, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from fetcher.adapters import list_adapters
from deduper.store import DedupStore
from notifier.telegram import TelegramNotifier
from scheduler.lock import make_lock
from scheduler.heartbeat import Heartbeat
from scheduler.sentry_reporter import SentryReporter

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("announcement")

async def _run_one(adapter, sem, store, notifier):
    async with sem:
        async with adapter as client:
            for item in await client.fetch():
                if store.add_if_new(item):
                    await notifier.send(item)
                    return 1
    return 0

async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="data/announcements.sqlite")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    lock_path = "/tmp/announcement.lock"
    lock = make_lock(
        redis_url=os.environ.get("LOCK_REDIS_URL"),
        file_path=lock_path,
    )
    with lock.acquire() as got:
        if not got:
            log.warning("another instance is running, exit")
            return 2

        hb = Heartbeat(os.environ.get("HEARTBEAT_URL"))
        reporter = SentryReporter(os.environ.get("SENTRY_DSN"))

        store = DedupStore(args.db)
        notifier = TelegramNotifier(
            token=os.environ.get("TELEGRAM_BOT_TOKEN", ""),
            chat_id=os.environ.get("TELEGRAM_CHAT_ID", ""),
            dry_run=args.dry_run,
        )
        sem = asyncio.Semaphore(2)
        new_count = 0
        try:
            coros = [_run_one(a, sem, store, notifier) for a in list_adapters()]
            results = await asyncio.gather(*coros)
            new_count = sum(results)
            log.info("done, new=%d", new_count)
            hb.ping("done")
            return 0
        except Exception:
            reporter.capture()
            log.exception("fatal")
            hb.fail("fatal")
            return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))