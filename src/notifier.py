from datetime import datetime
from pathlib import Path

ALERT_LOG = Path("data/alerts.log")

def notify(massage:str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}]{massage}"

    # Console notification
    print(formatted)

    # File notification
    ALERT_LOG.parent.mkdir(exist_ok=True)
    with ALERT_LOG.open("a", encoding="utf-8") as f:
        f.write(formatted + "\n")