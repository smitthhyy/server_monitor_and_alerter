'''
This application at a high level is a monitor and alert program.
As an overall monitor it needs to monitor:
    - Disk space alerting when disk usage is above a certain threshold
    - CPU usage alerting when CPU usage is above a certain threshold
    - Memory usage alerting when memory usage is above a certain threshold
    - Network traffic alerting when network traffic is above a certain threshold
    - Server status alerting when server status is down
It should also monitor key processes and alert when they are down. These processes are:
    - Apache HTTPD
    - Nginx
    - MySQL
    - PostgreSQL
    - Mosquitto
It should also monitor client applications which there are a number of and are in
unique folders per client with the same app running in multiple client environments
 (e.g. /home/client1/client_app1, /home/client2/client_app1, etc.)
Each monitoring process has a threshold value where if exceeded it sends an alert.
Alerts are sent via email using Amazon Simple Email Service (Amazon SES)
'''

import time
from config import config
from monitors.disk import DiskMonitor
from monitors.cpu import CpuMonitor
from monitors.memory import MemoryMonitor
from monitors.network import NetworkMonitor
from monitors.server import ServerMonitor
from monitors.process import ProcessMonitor
from monitors.client_app import ClientAppMonitor

def build_monitors():
    t = config.thresholds
    m = [
        DiskMonitor(t["disk_pct"]),
        CpuMonitor(t["cpu_pct"]),
        MemoryMonitor(t["mem_pct"]),
        NetworkMonitor(t["net_bytes"]),
        ServerMonitor(t["server_check_url"]),
        ProcessMonitor(t["processes"], min_count=1)
    ]
    for path, cnt in t["client_apps"].items():
        m.append(ClientAppMonitor(path, cnt))
    return m

def main():
    monitors = build_monitors()
    interval = config.interval
    while True:
        for mon in monitors:
            mon.run()
        time.sleep(interval)

if __name__ == "__main__":
    main()
