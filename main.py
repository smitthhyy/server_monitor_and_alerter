'''
This application at a high level is a monitor and alert program.
As an overall monitor it needs to watch:
    - Disk space (alert when usage > threshold)
    - CPU usage (alert when usage > threshold)
    - Memory usage (alert when usage > threshold)
    - Network traffic (alert when bytes/sec > threshold)
    - One or more server health endpoints (alert when non-200)
It also watches key processes (Apache, MySQL, Mosquitto, etc.)
and per-client apps in unique folders:
    e.g. /home/client1/client_app1, /home/client2/client_app1, etc.

Each monitor has its own threshold and sends alerts via Amazon SES.
'''

import logging
import time

from config import config
from monitors.disk import DiskMonitor
from monitors.cpu import CpuMonitor
from monitors.memory import MemoryMonitor
from monitors.network import NetworkMonitor
from monitors.server import ServerMonitor
from monitors.process import ProcessMonitor
from monitors.client_app import ClientAppMonitor

# 1) configure root logger
root_lvl = config.logging_cfg.get("root_level", "INFO")
logging.basicConfig(
    level=getattr(logging, root_lvl),
    format="%(asctime)s %(name)s %(levelname)s: %(message)s"
)

# 2) apply granular overrides
for logger_name, lvl_name in config.logging_cfg.get("overrides", {}).items():
    lvl = getattr(logging, lvl_name, None)
    if lvl is not None:
        logging.getLogger(logger_name).setLevel(lvl)

# 3) silence chatter from external libs if needed
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)

def build_monitors():
    t = config.thresholds
    monitors = [
        DiskMonitor(t["disk_pct"]),
        CpuMonitor(t["cpu_pct"]),
        MemoryMonitor(t["mem_pct"]),
        NetworkMonitor(t["net_bytes"]),
    ]

    # support multiple health-check URLs
    for url in t.get("server_check_urls", []):
        monitors.append(ServerMonitor(url))
    # backward-compat: single URL key
    if "server_check_url" in t:
        monitors.append(ServerMonitor(t["server_check_url"]))

    # key processes monitor
    # new: one monitor per process name
    for proc_name, min_cnt in config.thresholds["processes"].items():
        monitors.append(
            ProcessMonitor([proc_name], min_count=min_cnt)
        )

    # per-client app monitors: guard against None
    client_apps_cfg = t.get("client_apps") or {}
    for path, cnt in client_apps_cfg.items():
        monitors.append(ClientAppMonitor(path, cnt))

    return monitors

def main():
    monitors = build_monitors()
    interval = config.interval
    while True:
        for mon in monitors:
            mon.run()
        time.sleep(interval)

if __name__ == "__main__":
    main()
