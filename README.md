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

1. cd into /opt
2. `git clone https://github.com/smitthhyy/server_monitor_and_alerter.git
3. create a virtual environment using python3 -m venv /opt/server_monitor_and_alerter`
4. run `source /opt/server_monitor_and_alerter/bin/activate`
5. run `pip install -r /opt/server_monitor_and_alerter/requirements.txt`
6. Copy the config.example.yaml to config.yaml
7. Edit the config.yaml file to your needs
8. Make sure your in the /opt/server_monitor_and_alerter/bin directory
9. Run the application using `python3 main.py`

Once you are happy that everything is working the way you want, you can set up the systemctl file to run the app.

1. `cp server_monitor_and_alerter.service /etc/systemd/system`
2. `systemctl enable server_monitor_and_alerter.service`
3. `systemctl start server_monitor_and_alerter.service`

