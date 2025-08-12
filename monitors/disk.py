import logging
import psutil
from .base_monitor import BaseMonitor

logger = logging.getLogger(__name__)

class DiskMonitor(BaseMonitor):
    name = "DiskUsage"

    def __init__(self, threshold):
        super().__init__(threshold)

    def check(self):
        usage = psutil.disk_usage("/")
        pct = usage.percent
        breach = pct >= self.threshold
        logger.debug(
            "DiskMonitor.check → pct=%.1f, threshold=%s, breach=%s",
            pct, self.threshold, breach
        )
        return (breach, pct)

    def run(self):
        # capture state before BaseMonitor.run()
        status_before = getattr(self, "_last_status", None)
        err_before    = getattr(self, "_error_count", None)

        super().run()

        # log the transition & counter after
        logger.debug(
            "DiskMonitor.run: last_status=%s→%s, error_count=%d→%d",
            status_before, self._last_status,
            err_before,     self._error_count
        )
