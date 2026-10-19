import os
import tempfile

from deduper.store import DedupStore
from fetcher.base import AnnouncementItem


def test_add_new_returns_true_then_false():
    with tempfile.TemporaryDirectory() as d:
        store = DedupStore(os.path.join(d, "a.sqlite"))
        item = AnnouncementItem("school_a", "T", "u", "2026-10-18", "B")
        assert store.add_if_new(item) is True
        assert store.add_if_new(item) is False
        assert store.count() == 1

def test_different_body_means_new():
    with tempfile.TemporaryDirectory() as d:
        store = DedupStore(os.path.join(d, "a.sqlite"))
        a = AnnouncementItem("school_a", "T", "u", "2026-10-18", "B")
        b = AnnouncementItem("school_a", "T", "u", "2026-10-18", "B2")
        assert store.add_if_new(a) is True
        assert store.add_if_new(b) is True
