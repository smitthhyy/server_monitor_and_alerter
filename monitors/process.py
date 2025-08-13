import logging
import psutil
from .base_monitor import BaseMonitor

logger = logging.getLogger(__name__)

class ProcessMonitor(BaseMonitor):
    name = "Process"

    def __init__(self, proc_names, min_count=1):
        super().__init__(threshold=None)
        self.names = proc_names
        self.min_count = min_count

    def check(self):
        found = sum(
            1 for p in psutil.process_iter()
            if p.name() in self.names
        )
        logger.debug(
            "ProcessMonitor looking for %r → found %d (min_count=%d)",
            self.names, found, self.min_count
        )
        # breach == True means error (below minimum count)
        return (found < self.min_count, found)

    def run(self):
        status, value = self.check()

        if status:
            # increment failure count
            self._error_count += 1

            # send on first qualifying failure per configured consecutive cycles
            if (self._error_count == self.consecutive_required
                or self._error_count >= self._repeat_cycles):

                name_list = ", ".join(self.names)
                subject   = f"[ALERT] {self.name} ({name_list}) threshold exceeded"
                body      = f"{self.name} for [{name_list}] value={value}, min_count={self.min_count}"
                from alert import alerter
                alerter.send(subject, body)
                self._alert_sent = True

                # reset on repeat alert boundary
                if self._error_count >= self._repeat_cycles:
                    self._error_count = 0

        else:
            # only send recovery if we were previously in error AND an alert was sent
            if self._last_status and self._alert_sent:
                name_list = ", ".join(self.names)
                subject   = f"[RECOVERY] {self.name} ({name_list}) back to normal"
                body      = f"{self.name} for [{name_list}] value={value}, min_count={self.min_count}"
                from alert import alerter
                alerter.send(subject, body)
                self._alert_sent = False

            # reset counter whenever healthy
            self._error_count = 0

        # remember current status
        self._last_status = status
