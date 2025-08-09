import psutil
from .base_monitor import BaseMonitor

class ProcessMonitor(BaseMonitor):
    name = "Process"

    def __init__(self, proc_names, min_count=1):
        super().__init__(threshold=None)
        self.names = proc_names
        self.min_count = min_count

    def check(self):
        found = sum(1 for p in psutil.process_iter()
                    if p.name() in self.names)
        return (found < self.min_count, found)
