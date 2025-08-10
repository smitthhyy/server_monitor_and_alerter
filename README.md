# Server Monitor and Alerter

Copyright 2025 by Trevor van der Linden and licensed under MIT license

## Intro
A simple server monitor and alerter written in Python to monitor
and alert on servers specifically using Amazon AWS. It uses the
boto3 library to access SES and EC2.

It monitors the 
- CPU
- memory
- disk
- network
- specified services like apache2, mysql, etc.
- specific client applications with multiple same name apps on the server
- web addresses

When it detects an issue it sends an email to the specified email addresses.

## Installation

1. `cd /opt`
2. `git clone https://github.com/smitthhyy/server_monitor_and_alerter.git`
3. You may need to run `apt update; apt install python3.10-venv -y` before the next step
3. create a virtual environment using `python3 -m venv /opt/server_monitor_and_alerter`
4. `cd /opt/server_monitor_and_alerter`
4. run `source bin/activate`
5. run `pip install -r requirements.txt`
6. `cp config.example.yaml config.yaml`
7. Edit the config.yaml file to your needs
8. Make sure your in the /opt/server_monitor_and_alerter/bin directory
9. Run the application using `python3 main.py`

Once you are happy that everything is working the way you want, you can set up the systemctl file to run the app.

1. `cp server_monitor_and_alerter.service /etc/systemd/system`
2. `systemctl enable server_monitor_and_alerter.service`
3. `systemctl start server_monitor_and_alerter.service`

## Update the application from GitHub
Use the following commands to update the application from GitHub.

```
cd /opt/server_monitor_and_alerter
sudo git fetch origin main
sudo git reset --hard origin/main
sudo systemctl restart server_monitor_and_alerter.service
```
Success looks like:
```
root@s2.syd.example.com:/opt/server_monitor_and_alerter# git fetch origin main
remote: Enumerating objects: 24, done.
remote: Counting objects: 100% (24/24), done.
remote: Compressing objects: 100% (8/8), done.
remote: Total 17 (delta 11), reused 15 (delta 9), pack-reused 0 (from 0)
Unpacking objects: 100% (17/17), 2.77 KiB | 404.00 KiB/s, done.
From https://github.com/smitthhyy/server_monitor_and_alerter
 * branch            main       -> FETCH_HEAD
   a865fa5..5091f74  main       -> origin/main
root@s2.syd.example.com:/opt/server_monitor_and_alerter# git reset --hard origin/main
HEAD is now at 5091f74 anonymize subject_suffix
```

This fetches the latest code from the GitHub repository and resets the 
local repository to the latest code without overwriting the config.yaml file.
