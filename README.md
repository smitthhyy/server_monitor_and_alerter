# Server Monitor and Alerter

Copyright 2025 by Trevor van der Linden  
Licensed under the MIT License

## Overview
Server Monitor and Alerter is a lightweight Python application for monitoring Linux servers and sending alerts via AWS. It uses boto3 to integrate with Amazon EC2 (for instance metadata) and SES (for email).

Monitored items:
- CPU
- Memory
- Disk
- Network
- System services (e.g., apache2, mysql)
- Custom client applications (supports multiple processes with the same name)
- HTTP/HTTPS endpoints

Alerting behavior:
- CPU and Network: alert after 5 consecutive failures
- All others: alert after 1 failure

## Requirements
- Linux server with systemd (for optional service mode)
- Python 3.x with venv support
- AWS account with SES and (optionally) EC2 access
- Network access to AWS SES endpoints

## AWS Setup
Create AWS credentials (least-privilege recommended) and place them at:
- `/root/.aws/credentials` (or the runtime user’s home)

Example:
```
[default] 
aws_access_key_id = <YOUR_AWS_ACCESS_KEY_ID> 
aws_secret_access_key = <YOUR_AWS_SECRET_ACCESS_KEY>
```
Ensure the IAM user/role has permissions to send emails via SES (and read EC2 metadata if used).

## Installation
1. cd /opt
2. git clone https://github.com/smitthhyy/server_monitor_and_alerter.git
3. cd /opt/server_monitor_and_alerter
4. Ensure venv is available on your system (install if needed).
5. python3 -m venv .venv
6. source .venv/bin/activate
7. pip install -r requirements.txt
8. cp config.example.yaml config.yaml
9. Edit config.yaml to match your environment
10. Run locally to verify:
```
python3 main.py
```
## Configuration
- Primary configuration file: `config.yaml`
- A well-documented example is provided: `config.example.yaml`
- After changes to `config.yaml`, restart the application if running as a service.

## Run as a systemd Service (optional)
A sample unit file is provided at the project root: `server_monitor_and_alerter.service`. Review and adjust:
- User: Runtime user (often root if credentials are under /root)
- WorkingDirectory: Project directory (e.g., /opt/server_monitor_and_alerter)
- ExecStart: Use the venv interpreter, e.g., `/opt/server_monitor_and_alerter/.venv/bin/python3 /opt/server_monitor_and_alerter/main.py`
- Environment/logging settings as needed

Install and enable:
1. cp server_monitor_and_alerter.service /etc/systemd/system/
2. systemctl daemon-reload
3. systemctl enable server_monitor_and_alerter.service
4. systemctl start server_monitor_and_alerter.service
5. Check status/logs:
   - systemctl status server_monitor_and_alerter.service
   - journalctl -u server_monitor_and_alerter.service -f

## Updating
From the project directory as root user:
```
cd /opt/server_monitor_and_alerter 
git fetch origin main 
git reset --hard origin/main 
```
Example successful output:
```
root@s1:/opt/server_monitor_and_alerter# sudo git fetch origin main
remote: Enumerating objects: 7, done.
remote: Counting objects: 100% (7/7), done.
remote: Compressing objects: 100% (1/1), done.
remote: Total 4 (delta 3), reused 4 (delta 3), pack-reused 0 (from 0)
Unpacking objects: 100% (4/4), 780 bytes | 195.00 KiB/s, done.
From https://github.com/smitthhyy/server_monitor_and_alerter
 * branch            main       -> FETCH_HEAD
   ea42d25..21ab752  main       -> origin/main
root@s1:/opt/server_monitor_and_alerter# sudo git reset --hard origin/main
HEAD is now at 21ab752 Fix issue with cpu and network that if a single cycle has exceeded threshold and the next is below threshold, a RECOVERY email is sent. Now it will only send a recovery email if an alert was sent.
```
Then restart the service:
```
systemctl restart server_monitor_and_alerter.service
systemctl status server_monitor_and_alerter.service
```
It is a good idea to wait a minute and do the status again ensuring it's pid is the same (it's not having an error and restarting).
## Testing

- Make sure your virtual environment is activated and dependencies are installed.
- Tests use Python’s built-in unittest discovery and do not make real network/SES calls (email sending is mocked).

Run all tests:
- PowerShell/Windows:
```
python -m unittest discover -s tests -p "test_*.py"
```
- Bash/Linux/macOS (quote to prevent shell globbing):
```
python -m unittest discover -s tests -p 'test_*.py'
```
Useful options:
- Verbose output:
```
python -m unittest discover -s tests -p "test_*.py" -v
```
- Stop on first failure:
```
python -m unittest discover -s tests -p "test_*.py" -f
```
- Run a single test file:
```
python -m unittest tests/test_server_monitor.py
```
- Run a specific test case or method:
```
python -m unittest tests.test_server_monitor.ServerMonitorTests
python -m unittest tests.test_server_monitor.ServerMonitorTests.test_server_consecutive_cycles_and_recovery
```
Notes:
- If running in Bash, prefer single quotes around the pattern (e.g., 'test_*.py') so the shell doesn’t expand the wildcard.
- No additional setup is required for AWS in tests; email sending is patched out.

## Troubleshooting
- SES send failures:
  - Verify AWS credentials and SES region/verified identities
  - Check IAM permissions for ses:SendEmail
- No alerts received:
  - Inspect logs via systemd/journalctl
  - Confirm recipients and sender are correctly configured in config.yaml
- Service checks failing unexpectedly:
  - Validate service names and commands in the configuration
  - Ensure the monitoring user has permission to query system metrics/processes
- Configuration changes not applied:
  - Restart the service after edits: `systemctl restart server_monitor_and_alerter.service`

## Security Notes
- Store credentials securely (file permissions and least-privilege IAM)
- Restrict access to config.yaml if it contains sensitive settings
- Use environment variables or instance profiles where suitable

## License
MIT — see LICENSE file for details.
