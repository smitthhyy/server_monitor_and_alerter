import time
from alert import alerter
from config import config

class BaseMonitor:
    name = "base"
    # how many consecutive breaches before first alert
    consecutive_required = 1

    def __init__(self, threshold):
        self.threshold = threshold
        self._error_count = 0
        self._last_status = False
        self._repeat_cycles = config.thresholds.get("alert_repeat_cycles", 15)

    def check(self):
        raise NotImplementedError

    def run(self):
        status, value = self.check()

        if status:
            self._error_count += 1

            # first allowed alert at exactly consecutive_required
            # or at repeat intervals thereafter
            if (self._error_count == self.consecutive_required
                or self._error_count >= self._repeat_cycles):
                subject = f"[ALERT] {self.name} threshold exceeded"
                body = f"{self.name} value={value}, threshold={self.threshold}"
                alerter.send(subject, body)

                # if we're in the repeat stage, reset counter to 0
                if self._error_count >= self._repeat_cycles:
                    self._error_count = 0

        else:
            # recovery alert if we were previously in an error state
            if self._last_status:
                subject = f"[RECOVERY] {self.name} is back to normal"
                body = f"{self.name} value={value}, threshold={self.threshold}"
                alerter.send(subject, body)
            # reset counter any time we drop below threshold
            self._error_count = 0

        self._last_status = status
