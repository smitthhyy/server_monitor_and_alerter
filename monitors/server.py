import requests
from .base_monitor import BaseMonitor
from alert import alerter

class ServerMonitor(BaseMonitor):
    name = "ServerStatus"

    def __init__(self, url):
        super().__init__(threshold=None)
        self.url = url

    def check(self):
        try:
            r = requests.get(self.url, timeout=5)
            ok = (r.status_code == 200)
            code = r.status_code
        except Exception:
            ok = False
            code = "DOWN"
        return (not ok, code)

    def run(self):
        status, value = self.check()
        if status:
            subject = f"[ALERT] {self.name} ({self.url}) threshold exceeded"
            body = f"{self.name} check for '{self.url}' failed: returned {value}"
            alerter.send(subject, body)
