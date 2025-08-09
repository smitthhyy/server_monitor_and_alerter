import psutil
from .base_monitor import BaseMonitor

class CpuMonitor(BaseMonitor):
    name = "CPUUsage"
    def check(self):
        pct = psutil.cpu_percent(interval=1)
        return (pct >= self.threshold, pct)
