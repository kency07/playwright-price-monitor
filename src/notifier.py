import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

ALERT_LOG: Path = Path("data/alerts.log")
LAST_EMAIL_FILE: Path = Path("data/last_email_sent.txt")

EMAIL_ENABLED: bool = os.getenv("EMAIL_ENABLED", "false").lower() == "true"

SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
EMAIL_TO: Optional[str] = os.getenv("EMAIL_TO")

EMAIL_INTERVAL_SECONDS: int = int(os.getenv("EMAIL_INTERVAL_SECONDS", "900"))


def is_emai_config_valid() -> bool:
    """Check if all required email configuration values are set."""
    return all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_TO])


def can_send_email() -> bool:
    """
    Returns True if enough time has passed since the last email was sent.
    """
    if not LAST_EMAIL_FILE.exists():
        return True

    try:
        last_sent = float(LAST_EMAIL_FILE.read_text().strip())
        elapsed = datetime.now().timestamp() - last_sent
        return elapsed >= EMAIL_INTERVAL_SECONDS
    except Exception:
        # If file is corrupted, allow email
        return True


def record_email_sent() -> None:
    """Save current timestamp after sending email."""
    LAST_EMAIL_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAST_EMAIL_FILE.write_text(str(datetime.now().timestamp()))


def send_email(subject: str, body: str) -> None:
    """
    Send an email notification if email alerts are enabled
    and configuration is complete.
    """
    if not EMAIL_ENABLED:
        return

    if not is_emai_config_valid():
        print("Email settings are incomplete. Skipping email.")
        return

    if not can_send_email():
        print("Email rate limit reached. Skipping email.")
        return

    try:
        msg = EmailMessage()
        msg["From"] = SMTP_USER
        msg["To"] = EMAIL_TO
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        record_email_sent()

    except Exception as exc:
        print(f"Email sending failed: {exc}")


def notify(message: str, email: bool = False) -> None:
    """
    Log a notification message to console and file.
    Optionally send it via email.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}]  {message}"

    # Console notification
    print(formatted)

    # File notification
    try:
        ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with ALERT_LOG.open("a", encoding="utf-8") as f:
            f.write(formatted + "\n")

    except Exception as exc:
        print(f"Log write failed: {exc}")

    # Email(only if  requested)
    if email:
        send_email(subject="Price Monitor Alert", body=formatted)
