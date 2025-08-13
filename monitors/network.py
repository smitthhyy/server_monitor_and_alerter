import logging
import psutil
from .base_monitor import BaseMonitor

logger = logging.getLogger(__name__)

class NetworkMonitor(BaseMonitor):
    name = "NetworkTraffic"
    consecutive_required = 5

    def __init__(self, threshold):
        super().__init__(threshold)
        self._last = psutil.net_io_counters().bytes_recv + psutil.net_io_counters().bytes_sent

    def check(self):
        now = psutil.net_io_counters()
        total = now.bytes_recv + now.bytes_sent
        bps = total - self._last
        self._last = total

        breach = bps >= self.threshold
        logger.debug(
            "NetworkMonitor.check → bytes/sec=%d, threshold=%s, breach=%s",
            bps, self.threshold, breach
        )
        return (breach, bps)

    def run(self):
        status_before = getattr(self, "_last_status", None)
        err_before = getattr(self, "_error_count", None)
        super().run()
        logger.debug(
            "NetworkMonitor.run: last_status=%s→%s, error_count=%d→%d",
            status_before, self._last_status,
            err_before,   self._error_count
        )
