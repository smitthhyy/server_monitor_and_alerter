import logging
import psutil
from .base_monitor import BaseMonitor

# Toggle client‐app debug logging here:
ENABLE_DEBUG = False

logger = logging.getLogger(__name__)
if not ENABLE_DEBUG:
    # suppress DEBUG messages in this module
    logger.setLevel(logging.INFO)

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
        # duplicate BaseMonitor.run logic but inject process‐name into subject/body
        status, value = self.check()
        if status:
            # include the exact name(s) in the subject
            name_list = ", ".join(self.names)
            subject = f"[ALERT] {self.name} ({name_list}) threshold exceeded"
            body    = (
                f"{self.name} for [{name_list}] "
                f"value={value}, min_count={self.min_count}"
            )
            from alert import alerter
            alerter.send(subject, body)
            # handle repeat‐cycle logic exactly like BaseMonitor:
            self._error_count += 1
            if self._error_count >= self._repeat_cycles:
                self._error_count = 0
        else:
            # reset and optionally send recovery
            if self._last_status:
                name_list = ", ".join(self.names)
                subject = f"[RECOVERY] {self.name} ({name_list}) back to normal"
                body    = (
                    f"{self.name} for [{name_list}] "
                    f"value={value}, min_count={self.min_count}"
                )
                from alert import alerter
                alerter.send(subject, body)
            self._error_count = 0

        self._last_status = status

