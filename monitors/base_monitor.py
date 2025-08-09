import time
from alert import alerter

class BaseMonitor:
    name = "base"
    def __init__(self, threshold):
        self.threshold = threshold

    def check(self):
        raise NotImplementedError

    def run(self):
        status, value = self.check()
        if status:
            subject = f"[ALERT] {self.name} threshold exceeded"
            body = f"{self.name} value={value}, threshold={self.threshold}"
            alerter.send(subject, body)
