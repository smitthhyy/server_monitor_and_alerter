import requests
from .base_monitor import BaseMonitor

class ServerMonitor(BaseMonitor):
    name = "ServerStatus"
    def __init__(self, url):
        super().__init__(threshold=None)
        self.url = url

    def check(self):
        try:
            r = requests.get(self.url, timeout=5)
            ok = r.status_code == 200
        except Exception:
            ok = False
        return (not ok, r.status_code if ok else "DOWN")
