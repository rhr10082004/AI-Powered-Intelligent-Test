"""Small SMTP delivery helper for transactional account emails."""

from email.message import EmailMessage
import smtplib

from services.api.config import Settings


def send_transactional_email(settings: Settings, *, recipient: str, subject: str, body: str) -> bool:
    """Send a text email when SMTP is configured; report whether it was delivered."""
    if not settings.smtp_server or not settings.smtp_user or not settings.smtp_password:
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.sender_email
    message["To"] = recipient
    message.set_content(body)

    if settings.smtp_port == 465:
        with smtplib.SMTP_SSL(settings.smtp_server, settings.smtp_port, timeout=10) as server:
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(message)
    else:
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port, timeout=10) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(message)
    return True
