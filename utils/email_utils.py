import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from core.config import get_settings
settings = get_settings()

# Your SendGrid API Key
SENDGRID_API_KEY = settings.sendgrid_api_key
FROM_EMAIL = settings.sendgrid_from_email

# Admin + Team members who should receive the email
NOTIFY_USERS = [
    "gaurav@locktrust.com"
]


def send_email_sendgrid(subject: str, body: str, recipients: list):
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=recipients,
        subject=subject,
        html_content=body
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        print("Email sent successfully")
    except Exception as e:
        print("Error sending email:", e)