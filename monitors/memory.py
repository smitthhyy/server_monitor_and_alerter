import logging
import psutil
from .base_monitor import BaseMonitor

logger = logging.getLogger(__name__)

class MemoryMonitor(BaseMonitor):
    name = "MemUsage"

    def __init__(self, threshold):
        super().__init__(threshold)

    def check(self):
        mem = psutil.virtual_memory()
        pct = mem.percent
        breach = pct >= self.threshold
        logger.debug(
            "MemoryMonitor.check → pct=%.1f, threshold=%s, breach=%s",
            pct, self.threshold, breach
        )
        return (breach, pct)

    def run(self):
        # capture prior state
        status_before = getattr(self, "_last_status", None)
        err_before    = getattr(self, "_error_count", None)

        # invoke the BaseMonitor logic
        super().run()

        # log transition & counter changes
        logger.debug(
            "MemoryMonitor.run: last_status=%s→%s, error_count=%d→%d",
            status_before, self._last_status,
            err_before,     self._error_count
        )