import boto3
from botocore.exceptions import ClientError
from config import config

class EmailAlerter:
    def __init__(self):
        self.client = boto3.client("ses", region_name=config.aws["region"])
        self.sender = config.aws["ses_sender"]
        self.recipients = config.aws["ses_recipients"]

    def send(self, subject: str, body: str):
        try:
            self.client.send_email(
                Source=self.sender,
                Destination={"ToAddresses": self.recipients},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {"Text": {"Data": body}}
                }
            )
        except ClientError as e:
            print(f"SES send error: {e}")

alerter = EmailAlerter()
