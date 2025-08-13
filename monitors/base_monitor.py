import time
from alert import alerter
from config import config

class BaseMonitor:
    name = "base"
    consecutive_required = 1

    def __init__(self, threshold):
        self.threshold      = threshold
        self._error_count   = 0
        self._last_status   = False
        self._repeat_cycles = config.thresholds.get("alert_repeat_cycles", 15)
        # track if we've actually sent an alert in this error streak
        self._alert_sent    = False

        # Allow per-monitor override from config.thresholds.alert_consecutive_cycles
        cycles_map = (config.thresholds.get("alert_consecutive_cycles") or {})
        default_required = getattr(self.__class__, "consecutive_required", 1)
        self.consecutive_required = int(cycles_map.get(self.name, default_required))

    def check(self):
        raise NotImplementedError

    def run(self):
        status, value = self.check()

        if status:
            self._error_count += 1

            if not self._alert_sent:
                # First alert only when we reach the consecutive_required threshold
                if self._error_count == self.consecutive_required:
                    subject = f"[ALERT] {self.name} threshold exceeded"
                    body    = f"{self.name} value={value}, threshold={self.threshold}"
                    alerter.send(subject, body)
                    self._alert_sent = True
            else:
                # After first alert, only send alerts on repeat boundaries
                if self._error_count >= self._repeat_cycles:
                    subject = f"[ALERT] {self.name} threshold exceeded"
                    body    = f"{self.name} value={value}, threshold={self.threshold}"
                    alerter.send(subject, body)
                    # reset counter after a repeat alert
                    self._error_count = 0

        else:
            # only send recovery if we previously sent an alert
            if self._last_status and self._alert_sent:
                subject = f"[RECOVERY] {self.name} is back to normal"
                body    = f"{self.name} value={value}, threshold={self.threshold}"
                alerter.send(subject, body)
                # now clear the alert flag
                self._alert_sent = False

            # reset the error count whenever healthy
            self._error_count = 0

        # record status for next cycle
        self._last_status = status
