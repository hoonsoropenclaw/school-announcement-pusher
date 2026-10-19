"""SQLite-backed deduper: stores URL + sha256(title+date+body)."""
import sqlite3
import threading

from fetcher.base import AnnouncementItem


class DedupStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._lock = threading.Lock()
        import os as _os
        _os.makedirs(_os.path.dirname(db_path) or ".", exist_ok=True)
        with self._conn() as cx:
            cx.execute(
                "CREATE TABLE IF NOT EXISTS seen ("
                "  fp TEXT PRIMARY KEY,"
                "  url TEXT NOT NULL,"
                "  title TEXT NOT NULL,"
                "  date TEXT NOT NULL,"
                "  school TEXT NOT NULL,"
                "  first_seen TEXT NOT NULL DEFAULT (datetime('now'))"
                ")"
            )
            cx.commit()

    def _conn(self):
        c = sqlite3.connect(self.db_path, isolation_level=None)
        c.row_factory = sqlite3.Row
        return c

    def add_if_new(self, item: AnnouncementItem) -> bool:
        fp = item.fingerprint()
        with self._lock, self._conn() as cx:
            row = cx.execute("SELECT 1 FROM seen WHERE fp=?", (fp,)).fetchone()
            if row:
                return False
            cx.execute(
                "INSERT INTO seen(fp,url,title,date,school) VALUES (?,?,?,?,?)",
                (fp, item.url, item.title, item.date, item.school),
            )
            return True

    def count(self) -> int:
        with self._conn() as cx:
            return cx.execute("SELECT COUNT(*) c FROM seen").fetchone()["c"]
