import asyncio
import logging
import os
import smtplib
from email.message import EmailMessage
from time import time
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
_EMAIL_QUEUE = []

LAST_EMAIL_FILE: Path = Path("data/last_email_sent.txt")

EMAIL_ENABLED: bool = os.getenv("EMAIL_ENABLED", "false").lower() == "true"

SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
EMAIL_TO: Optional[str] = os.getenv("EMAIL_TO")

EMAIL_INTERVAL_SECONDS: int = int(os.getenv("EMAIL_INTERVAL_SECONDS", "900"))


def is_emaiL_config_valid() -> bool:
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
        elapsed = time() - last_sent
        return elapsed >= EMAIL_INTERVAL_SECONDS
    except Exception as exc:
        logging.warning(
            f"Email timestamp file corrupted: {exc}"
        )  # If file is corrupted, allow email
        return True


def record_email_sent() -> None:
    """Save current timestamp after sending email."""
    LAST_EMAIL_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAST_EMAIL_FILE.write_text(str(time()))


def _perform_actual_send(subject: str, body: str) -> None:
    """
    Send an email notification if email alerts are enabled
    and configuration is complete.
    """

    if not is_emaiL_config_valid():
        logging.error("Email settings are incomplete. Skipping email.")
        return

    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)


def flush_email_queue() -> None:
    """
    Sends all queued messages in one single email if the rate limit allows.
    """
    global _EMAIL_QUEUE

    if not _EMAIL_QUEUE:
        return
    if not EMAIL_ENABLED:
        _EMAIL_QUEUE.clear()
        return 

    if not can_send_email():
        logging.info(f"Email rate limit activ. {len(_EMAIL_QUEUE)} alerts pending.")
        return
    # Combine all messages into one body
    email_body = "\n".join(_EMAIL_QUEUE)
    subject = f"Price Monitor Alert:{len(_EMAIL_QUEUE)} update"

    try:
        _perform_actual_send(subject, email_body)
        _EMAIL_QUEUE.clear()
        record_email_sent()
        logging.info("Batch email sent successfully")
    except Exception:
        logging.exception(f"Email sending failed")


async def email_manager():
    """
    Background task to periodically check and send queued emails.
    """
    while True:
        try:
            flush_email_queue()
        except Exception:
            logging.exception("email manager crashed")   
        await asyncio.sleep(60)


def notify(message: str, email: bool = False) -> None:
    """
    Log a notification message to console and file.
    Optionally queue it for email.
    """
    logging.info(message)

    # Email(only if  requested)
    if email:
        _EMAIL_QUEUE.append(message)
