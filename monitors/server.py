import requests
from .base_monitor import BaseMonitor
from alert import alerter
import logging

# Toggle client‐app debug logging here:
ENABLE_DEBUG = False

logger = logging.getLogger(__name__)
if not ENABLE_DEBUG:
    # suppress DEBUG messages in this module
    logger.setLevel(logging.INFO)

class ServerMonitor(BaseMonitor):
    name = "ServerStatus"

    def __init__(self, url):
        super().__init__(threshold=None)
        self.url = url
        logger.debug("Initialized ServerMonitor: url=%s", self.url)
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
        # bump the counter first
        self._error_count += 1

        # send only on 1st error or once per repeat‐cycle
        if self._error_count == 1 or self._error_count >= self._repeat_cycles:
            name_list = ", ".join(self.names)
            subject   = f"[ALERT] {self.name} ({name_list}) threshold exceeded"
            body      = f"{self.name} for [{name_list}] value={value}, min_count={self.min_count}"
            from alert import alerter
            alerter.send(subject, body)

            # reset after sending a repeat alert
            if self._error_count >= self._repeat_cycles:
                self._error_count = 0

    else:
        # reset and optionally send recovery
        if self._last_status:
            name_list = ", ".join(self.names)
            subject   = f"[RECOVERY] {self.name} ({name_list}) back to normal"
            body      = f"{self.name} for [{name_list}] value={value}, min_count={self.min_count}"
            from alert import alerter
            alerter.send(subject, body)

        # reset error count on any healthy cycle
        self._error_count = 0

    # record status for next cycle
    self._last_status = status

