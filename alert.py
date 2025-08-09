import boto3
from botocore.exceptions import ClientError
from config import config

class EmailAlerter:
    def __init__(self):
        self.client     = boto3.client("ses", region_name=config.aws["region"])
        self.sender     = config.aws["ses_sender"]
        self.recipients = config.aws["ses_recipients"]

    def send(self, subject: str, body: str):
        # if a suffix is configured, inject it after the [ALERT] or [RECOVERY] tag
        suffix = config.subject_suffix
        if suffix:
            for tag in ("[ALERT]", "[RECOVERY]"):
                if subject.startswith(tag):
                    # only replace the first occurrence
                    subject = subject.replace(tag, f"{tag}{suffix}", 1)
                    break

        try:
            self.client.send_email(
                Source      = self.sender,
                Destination = {"ToAddresses": self.recipients},
                Message     = {
                    "Subject": {"Data": subject},
                    "Body"   : {"Text": {"Data": body}}
                }
            )
        except ClientError as e:
            print(f"SES send error: {e}")

alerter = EmailAlerter()
