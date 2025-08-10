import time
from alert import alerter
from config import config

class BaseMonitor:
    name = "base"

    def __init__(self, threshold):
        self.threshold = threshold
        # track consecutive error counts and last run status
        self._error_count = 0
        self._last_status = False
        # how many cycles to wait before re-alerting on a persistent error
        self._repeat_cycles = config.thresholds.get("alert_repeat_cycles", 15)

    def check(self):
        raise NotImplementedError

    def run(self):
        status, value = self.check()

        # error case
        if status:
            self._error_count += 1
            # first occurrence or reached repeat threshold
            if self._error_count == 1 or self._error_count >= self._repeat_cycles:
                subject = f"[ALERT] {self.name} threshold exceeded"
                body = f"{self.name} value={value}, threshold={self.threshold}"
                alerter.send(subject, body)
                # reset count if we're sending a repeat alert
                if self._error_count >= self._repeat_cycles:
                    self._error_count = 0

        # recovery case
        else:
            # if previously in error, alert that we're back to normal
            if self._last_status:
                subject = f"[RECOVERY] {self.name} is back to normal"
                body = f"{self.name} value={value}, threshold={self.threshold}"
                alerter.send(subject, body)
            # reset error counter on any healthy cycle
            self._error_count = 0

        # record status for next cycle
        self._last_status = status

