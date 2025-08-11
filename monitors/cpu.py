import psutil
from .base_monitor import BaseMonitor

class CpuMonitor(BaseMonitor):
    name = "CPUUsage"
    consecutive_required = 2

    def check(self):
        pct = psutil.cpu_percent(interval=1)
        return (pct >= self.threshold, pct)

