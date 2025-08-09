import psutil, os
from .base_monitor import BaseMonitor

class ClientAppMonitor(BaseMonitor):
    name = "ClientApp"

    def __init__(self, path, min_procs):
        super().__init__(threshold=None)
        self.path = path
        self.min_procs = min_procs

    def check(self):
        cnt = 0
        for p in psutil.process_iter(attrs=["cwd"]):
            try:
                if os.path.abspath(p.info["cwd"]) == self.path:
                    cnt += 1
            except Exception:
                continue
        return (cnt < self.min_procs, cnt)
