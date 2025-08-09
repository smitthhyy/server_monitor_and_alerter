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
        # normalize to absolute folder path
        self.path = os.path.abspath(path)
        self.min_procs = min_procs
        logger.debug(
            "Initialized ClientAppMonitor: path=%s, min_procs=%d",
            self.path, self.min_procs
        )

    def check(self):
        cnt = 0
        for p in psutil.process_iter(attrs=["pid", "cwd", "cmdline"]):
            info = p.info
            cwd = info.get("cwd")
            cmd = info.get("cmdline") or []
            logger.debug(
                "PID %s: cwd=%r, cmdline=%r",
                info.get("pid"), cwd, cmd
            )
            try:
                # 1) direct cwd match
                if cwd and os.path.abspath(cwd) == self.path:
                    cnt += 1
                    logger.debug(" → match by cwd (count=%d)", cnt)

                # 2) or script path (resolve relative to cwd)
                elif cwd and len(cmd) > 1:
                    script = cmd[1]
                    full = os.path.abspath(os.path.join(cwd, script))
                    # match exact folder or any sub‐directory/file under it
                    if full == self.path or full.startswith(self.path + os.sep):
                        cnt += 1
                        logger.debug(
                            " → match by script path %r (count=%d)",
                            full, cnt
                        )

            except (IndexError, TypeError, FileNotFoundError) as e:
                logger.debug(
                    " → skipped pid %s due to %s",
                    info.get("pid"), e
                )

        logger.debug("Total processes found under %s: %d", self.path, cnt)
        # return True to alert when count < min_procs
        return (cnt < self.min_procs, cnt)
