"""Pluggable lock backend: fcntl (default) or Redis SET NX EX."""
import contextlib
import fcntl
import logging
import os
import time

log = logging.getLogger("lock")


class FcntlLock:
    def __init__(self, path: str):
        self.path = path

    @contextlib.contextmanager
    def acquire(self):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        f = open(self.path, "w")
        try:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                yield True
            except BlockingIOError:
                yield False
        finally:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            except Exception:
                pass
            f.close()


class RedisLock:
    def __init__(self, redis_url: str, key: str = "announcement:lock", ttl: int = 600):
        import redis as _redis
        self._r = _redis.from_url(redis_url, decode_responses=True)
        self._key = key
        self._ttl = ttl
        self._token = f"{os.getpid()}-{time.time()}"

    @contextlib.contextmanager
    def acquire(self):
        got = self._r.set(self._key, self._token, nx=True, ex=self._ttl)
        if not got:
            yield False
            return
        try:
            yield True
        finally:
            # release only if we still own it
            lua = """
            if redis.call('get', KEYS[1]) == ARGV[1] then
                return redis.call('del', KEYS[1])
            end
            return 0
            """
            try:
                self._r.eval(lua, 1, self._key, self._token)
            except Exception:
                log.warning("redis lock release failed", exc_info=True)


def make_lock(redis_url: str | None = None, file_path: str | None = None):
    """Factory: prefer Redis if URL set, else fall back to fcntl."""
    if redis_url:
        return RedisLock(redis_url)
    if file_path is None:
        file_path = "/tmp/announcement.lock"
    return FcntlLock(file_path)


# Backwards compatibility for callers using the old function:
@contextlib.contextmanager
def acquire_lock(path: str):
    lock = make_lock(file_path=path)
    with lock.acquire() as ok:
        yield ok
