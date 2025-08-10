import os
import psutil
import logging
from .base_monitor import BaseMonitor

# Toggle client‐app debug logging here:
ENABLE_DEBUG = False

logger = logging.getLogger(__name__)
if not ENABLE_DEBUG:
    # suppress DEBUG messages in this module
    logger.setLevel(logging.INFO)

class ClientAppMonitor(BaseMonitor):
    name = "ClientApp"

    def __init__(self, path, min_procs):
        super().__init__(threshold=None)
        self.path = os.path.abspath(path)
        self.min_procs = min_procs
        logger.debug(
            "Initialized ClientAppMonitor: path=%s, min_procs=%d",
            self.path, self.min_procs
        )

    def check(self):
        cnt = 0
        for p in psutil.process_iter():
            try:
                cmd = p.cmdline()
                cwd = p.cwd()
            except (psutil.Error, FileNotFoundError):
                continue

            logger.debug("PID %s: cwd=%r, cmdline=%r", p.pid, cwd, cmd)

            # 1) match by cwd
            if cwd and os.path.abspath(cwd) == self.path:
                cnt += 1
                logger.debug(" → match by cwd (count=%d)", cnt)
                continue

            # 2) match by script path
            script = None

            # case A: cmd[0] is like "node /full/path/to/app.js"
            if cmd and isinstance(cmd[0], str) and cmd[0].startswith("node "):
                parts = cmd[0].split(None, 1)
                if len(parts) == 2:
                    script = parts[1]

            # case B: proper argv list, script in cmd[1]
            elif len(cmd) > 1 and cmd[0].endswith("node"):
                script = cmd[1]

            if script:
                full = os.path.abspath(os.path.join(cwd, script))
                if full == self.path or full.startswith(self.path + os.sep):
                    cnt += 1
                    logger.debug(" → match by script path %r (count=%d)", full, cnt)

        logger.debug("Total processes found under %s: %d", self.path, cnt)
        return (cnt < self.min_procs, cnt)


    def run(self):
        status, value = self.check()

        if status:
            # bump the error counter first
            self._error_count += 1
            # send only on first error or at repeat threshold
            if self._error_count == 1 or self._error_count >= self._repeat_cycles:
                subject = f"[ALERT] {self.name} ({self.path}) threshold exceeded"
                body    = f"{self.name} for [{self.path}] value={value}, min_procs={self.min_procs}"
                from alert import alerter
                alerter.send(subject, body)
                # reset on repeat alert
                if self._error_count >= self._repeat_cycles:
                    self._error_count = 0

        else:
            # on recovery, only alert if we were previously in error
            if self._last_status:
                subject = f"[RECOVERY] {self.name} ({self.path}) back to normal"
                body    = f"{self.name} for [{self.path}] value={value}, min_procs={self.min_procs}"
                from alert import alerter
                alerter.send(subject, body)
            self._error_count = 0

        # record status for next cycle
        self._last_status = status


