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
### Get AWS credentials
You will need to get AWS credentials to use this application. You can get them from the AWS console.
The recomended method is to create the /root/.aws/credentials file with the following content
changing the values to your own:
```
[default]           
aws_access_key_id = ABCDEFGHIJKLMNOPQRST
aws_secret_access_key = abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN
```                     
### Install the application
Use the following commands to install the application.

1. `cd /opt`
2. `git clone https://github.com/smitthhyy/server_monitor_and_alerter.git`
3. You may need to run `apt update; apt install python3.10-venv -y` before the next step. Note some systems
may call it python3-venv.
3. create a virtual environment using `python3 -m venv /opt/server_monitor_and_alerter`
4. `cd /opt/server_monitor_and_alerter`
4. run `source bin/activate`
5. run `pip install -r requirements.txt`
6. `cp config.example.yaml config.yaml`
7. Edit the config.yaml file to your needs
8. Make sure your in the /opt/server_monitor_and_alerter/bin directory
9. Run the application using `python3 main.py`

Once you are happy that everything is working the way you want, you can set up the systemd file to run the app.

The file is called server_monitor_and_alerter.service and is located in the /opt/server_monitor_and_alerter directory.
It will need to be modified to match your environment. The various settings are:
- User: The user to run the application as. This is usually root if that is the user that has the AWS credentials.
- WorkingDirectory: The directory to run the application from
- ExecStart: The command to run the application
- Restart: The restart policy for the application
- Environment: The environment variables to set for the application
- StandardOutput: The file to log the application output to
- StandardError: The file to log the application error to
- SyslogIdentifier: The name of the application in syslog
- Description: A description of the application
- Wants: The other services that this application depends on

The following commands will copy the file to the correct location and enable the service.
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

#Configure the application
The configuration for this application is in the config.yaml file.
There is a sample config.yaml file called config.example.yaml in the repository which is well documented. 

Changes to config.yaml will require a restart of the application with `systemctl restart server_monitor_and_alerter.service`

