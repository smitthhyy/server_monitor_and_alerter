import logging
import requests
from .base_monitor import BaseMonitor
from alert import alerter

logger = logging.getLogger(__name__)

class ServerMonitor(BaseMonitor):
    name = "ServerStatus"

    def __init__(self, url):
        super().__init__(threshold=None)
        self.url = url
        # Include the URL in the displayed name for alert/recovery emails.
        # Note: BaseMonitor reads alert_consecutive_cycles at __init__, so changing
        # self.name here won't affect your config mapping for "ServerStatus".
        self.name = f"ServerStatus {self.url}"
        logger.debug("ServerMonitor initialized with url=%s", self.url)


    def check(self):
        try:
            r = requests.get(self.url, timeout=5)
            ok = (r.status_code == 200)
            code = r.status_code
        except Exception:
            ok = False
            code = "DOWN"

        # note: status=True means “error” in BaseMonitor
        breach = not ok
        logger.debug(
            "ServerMonitor.check → url=%s, status_code=%s, breach=%s",
            self.url, code, breach
        )
        return (breach, code)

    def run(self):
        # capture state before
        status_before = getattr(self, "_last_status", None)
        err_before    = getattr(self, "_error_count", None)

        super().run()

        # log transition & counter changes
        logger.debug(
            "ServerMonitor.run: last_status=%s→%s, error_count=%d→%d",
            status_before, self._last_status,
            err_before,     self._error_count
        )

