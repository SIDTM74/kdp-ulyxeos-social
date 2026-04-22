import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import (
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD,
    SMTP_FROM, ADMIN_NOTIFICATION_EMAIL
)


def send_social_report_email(subject: str, body: str, to_email: str | None = None) -> None:
    recipient = to_email or ADMIN_NOTIFICATION_EMAIL

    if not SMTP_HOST or not SMTP_FROM:
        print("Email skipped: SMTP not configured.")
        return

    msg = MIMEMultipart()
    msg["From"] = SMTP_FROM
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        if SMTP_USER and SMTP_PASSWORD:
            server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM, recipient, msg.as_string())