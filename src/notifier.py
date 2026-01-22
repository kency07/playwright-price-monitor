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
MAX_EMAIL_QUEUE = 100
SMTP_FAILURES = 0
MAX_SMTP_FAILURES = 5


LAST_EMAIL_FILE: Path = Path("data/last_email_sent.txt")

EMAIL_ENABLED: bool = os.getenv("EMAIL_ENABLED", "false").lower() == "true"

SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
EMAIL_TO: Optional[str] = os.getenv("EMAIL_TO")

EMAIL_INTERVAL_SECONDS: int = int(os.getenv("EMAIL_INTERVAL_SECONDS", "900"))


def is_email_config_valid() -> bool:
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
    global SMTP_FAILURES
    if not is_email_config_valid():
        logging.error("Email settings are incomplete. Skipping email.")
        _EMAIL_QUEUE.clear()
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

        SMTP_FAILURES = 0 # success → reset
    except smtplib.SMTPAuthenticationError:
         # PERMANENT until user fixes config
         SMTP_FAILURES += 1
         logging.error("SMTP authentication failed. Disabling email alerts.")
         _EMAIL_QUEUE.clear()
         raise
    except smtplib.SMTPException as e:
        SMTP_FAILURES += 1
        logging.warning("Temporary SMTP error: %s", e)


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

    if SMTP_FAILURES >= MAX_SMTP_FAILURES:
        logging.error("SMTP appears broken. Disabling email alerts.")
        _EMAIL_QUEUE.clear()
        return
    if not can_send_email():
        logging.info(f"Email rate limit active. {len(_EMAIL_QUEUE)} alerts pending.")
        return
    # Combine all messages into one body
    email_body = "\n".join(_EMAIL_QUEUE)
    subject = f"Price Monitor Alert: {len(_EMAIL_QUEUE)} updates"

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
        except asyncio.CancelledError:
            logging.info("email manager stopped")
            raise
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
        if len(_EMAIL_QUEUE) >= MAX_EMAIL_QUEUE:
            logging.warning("Email queue full. Dropping oldest alert.")
            _EMAIL_QUEUE.pop(0)
        _EMAIL_QUEUE.append(message)
