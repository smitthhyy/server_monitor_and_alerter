import logging
import psutil
from .base_monitor import BaseMonitor

logger = logging.getLogger(__name__)

class CpuMonitor(BaseMonitor):
    name = "CPUUsage"
    consecutive_required = 2

    def check(self):
        pct = psutil.cpu_percent(interval=1)
        breach = pct >= self.threshold
        logger.debug(
            "CpuMonitor.check → pct=%.1f, threshold=%s, breach=%s",
            pct, self.threshold, breach
        )
        return (breach, pct)

    # inherit BaseMonitor.run, but we want a hook to log its state after run:
    def run(self):
        status_before = getattr(self, "_last_status", None)
        err_before = getattr(self, "_error_count", None)
        super().run()
        logger.debug(
            "CpuMonitor.run: last_status=%s→%s, error_count=%d→%d",
            status_before, self._last_status,
            err_before,   self._error_count
        )


