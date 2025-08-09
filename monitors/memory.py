import psutil
from .base_monitor import BaseMonitor

class MemoryMonitor(BaseMonitor):
    name = "MemUsage"
    def check(self):
        mem = psutil.virtual_memory()
        pct = mem.percent
        return (pct >= self.threshold, pct)
