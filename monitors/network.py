import psutil, time
from .base_monitor import BaseMonitor

class NetworkMonitor(BaseMonitor):
    name = "NetTraffic"
    def __init__(self, threshold):
        super().__init__(threshold)
        self.prev = psutil.net_io_counters()

    def check(self):
        time.sleep(1)
        curr = psutil.net_io_counters()
        sent = curr.bytes_sent - self.prev.bytes_sent
        recv = curr.bytes_recv - self.prev.bytes_recv
        total = sent + recv
        self.prev = curr
        return (total >= self.threshold, total)
