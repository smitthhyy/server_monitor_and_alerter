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
        # add this debug line:
        logger.debug(
            "ProcessMonitor looking for %r → found %d (min_count=%d)",
            self.names, found, self.min_count
        )
        return (found < self.min_count, found)

    def run(self):
        status, value = self.check()

        if status:
            # 1) increment the counter
            self._error_count += 1

            # 2) send only on first error or at repeat threshold
            if self._error_count == 1 or self._error_count >= self._repeat_cycles:
                name_list = ", ".join(self.names)
                subject   = f"[ALERT] {self.name} ({name_list}) threshold exceeded"
                body      = f"{self.name} for [{name_list}] value={value}, min_count={self.min_count}"
                from alert import alerter
                alerter.send(subject, body)

                # 3) reset on repeat‐alert
                if self._error_count >= self._repeat_cycles:
                    self._error_count = 0

        else:
            # recovery path: only send if we were previously in error
            if self._last_status:
                name_list = ", ".join(self.names)
                subject   = f"[RECOVERY] {self.name} ({name_list}) back to normal"
                body      = f"{self.name} for [{name_list}] value={value}, min_count={self.min_count}"
                from alert import alerter
                alerter.send(subject, body)

            # reset counter whenever healthy
            self._error_count = 0

        # remember current status
        self._last_status = status
