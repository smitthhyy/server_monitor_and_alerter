import os
import psutil
import logging
from .base_monitor import BaseMonitor

logger = logging.getLogger(__name__)

class ClientAppMonitor(BaseMonitor):
    name = "ClientApp"

    def __init__(self, path, min_procs):
        super().__init__(threshold=None)
        self.path = os.path.abspath(path)
        self.min_procs = min_procs
        logger.debug(
            "ClientAppMonitor initialized: path=%s, min_procs=%d",
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
            # match by cwd
            if cwd and os.path.abspath(cwd) == self.path:
                cnt += 1
                logger.debug(" → match by cwd (count=%d)", cnt)
                continue

            # match by script path
            script = None
            if cmd and isinstance(cmd[0], str) and cmd[0].startswith("node "):
                parts = cmd[0].split(None, 1)
                if len(parts) == 2:
                    script = parts[1]
            elif len(cmd) > 1 and cmd[0].endswith("node"):
                script = cmd[1]

            if script:
                full = os.path.abspath(os.path.join(cwd, script))
                if full == self.path or full.startswith(self.path + os.sep):
                    cnt += 1
                    logger.debug(" → match by script path %r (count=%d)", full, cnt)

        # summary debug
        breach = cnt < self.min_procs
        logger.debug(
            "ClientAppMonitor.check → path=%s, procs_found=%d, min_procs=%d, breach=%s",
            self.path, cnt, self.min_procs, breach
        )
        return (breach, cnt)

    def run(self):
        # capture state before BaseMonitor.run()
        status_before = getattr(self, "_last_status", None)
        err_before    = getattr(self, "_error_count", None)

        # invoke the core logic
        super().run()

        # log after
        logger.debug(
            "ClientAppMonitor.run: last_status=%s→%s, error_count=%d→%d",
            status_before, self._last_status,
            err_before,     self._error_count
        )
