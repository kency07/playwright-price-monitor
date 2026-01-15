import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

ALERT_LOG:Path = Path("data/alerts.log")

EMAIL_ENABLED:bool = os.getenv("EMAIL_ENABLED", "false").lower() == "true"

SMTP_HOST :Optional[str] = os.getenv("SMTP_HOST")
SMTP_PORT:int = int(os.getenv("SMTP_PORT", 587))
SMTP_USER:Optional[str] = os.getenv("SMTP_USER")
SMTP_PASSWORD:Optional[str] = os.getenv("SMTP_PASSWORD")
EMAIL_TO:Optional[str] = os.getenv("EMAIL_TO")

def is_emai_config_valid()->bool:
    """Check if all required email configuration values are set."""
    return all([SMTP_HOST,SMTP_PORT,SMTP_USER,SMTP_PASSWORD,EMAIL_TO])

def send_email(subject:str, body:str)->None:

     """
    Send an email notification if email alerts are enabled
    and configuration is complete.
    """
     if not EMAIL_ENABLED:
        return
     if not is_emai_config_valid():
         print("Email settings are incomplete. Skipping email.")
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
    
     except Exception as exc:
         print(f"Email sending failed: {exc}")

def notify(message:str, email:bool=False)->None:
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

    #Email(only if  requested)
    if email:
        send_email(
            subject="Price Monitor Alert",
            body=formatted
            )