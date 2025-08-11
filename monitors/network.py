import psutil
from .base_monitor import BaseMonitor

class NetworkMonitor(BaseMonitor):
    name = "NetworkTraffic"
    consecutive_required = 2

    def __init__(self, threshold):
        super().__init__(threshold)
        # measure over 1 second; store previous total
        self._last = psutil.net_io_counters().bytes_recv + psutil.net_io_counters().bytes_sent

    def check(self):
        now = psutil.net_io_counters()
        total = now.bytes_recv + now.bytes_sent
        # bytes/sec since last call
        bps = (total - self._last)
        self._last = total
        return (bps >= self.threshold, bps)
