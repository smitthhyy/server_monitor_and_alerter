import psutil
from .base_monitor import BaseMonitor

class DiskMonitor(BaseMonitor):
    name = "DiskUsage"

    def __init__(self, threshold):
        super().__init__(threshold)

    def check(self):
        usage = psutil.disk_usage("/")
        pct = usage.percent
        return (pct >= self.threshold, pct)
