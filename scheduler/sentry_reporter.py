"""Thin Sentry wrapper; no-op when DSN missing."""
import logging

log = logging.getLogger("sentry")

class SentryReporter:
    def __init__(self, dsn: str | None):
        self.dsn = dsn

    def capture(self) -> None:
        if not self.dsn:
            log.warning("sentry disabled")
            return
        try:
            import sentry_sdk
            sentry_sdk.capture_exception()
        except Exception:
            log.warning("sentry init failed", exc_info=True)
