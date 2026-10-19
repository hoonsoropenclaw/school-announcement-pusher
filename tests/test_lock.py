import tempfile

from scheduler.lock import acquire_lock


def test_second_lock_blocked():
    with tempfile.TemporaryDirectory() as d:
        path = f"{d}/x.lock"
        with acquire_lock(path) as a:
            assert a is True
            with acquire_lock(path) as b:
                assert b is False
