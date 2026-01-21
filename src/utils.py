import re
from typing import Optional
import socket
import sys
import logging


def is_connected():
    try:

        socket.create_connection(("8.8.8.8", 53), timeout=3).close()
        return True
    except OSError:
        logging.critical("No internet connection detected, exiting")
        sys.exit(1)


def normalized_price(price_text: str) -> Optional[float]:
    """
    Extract numeric price from strings like:
    ₹8,299 | $12.5 | €13 | 123 | 23.0
    """
    # case 1: invalid or empty
    if not isinstance(price_text, str) or not price_text.strip():
        return None
    # Remove currency symbols and spaces
    # case2: string price
    price_text = price_text.replace(",", "")
    match = re.search(r"\d+(?:\.\d+)?", price_text)

    return float(match.group()) if match else None
