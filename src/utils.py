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
        logging.critical(
            "No internet connection detected. Program cannot function without it."
        )
        sys.exit(1)


def validate_products(products):
    ids = [product["id"] for product in products]

    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate product IDs detected!")
    for product in products:
        required = {"id", "url", "price_selector"}
        missing = required - product.keys()

        if missing:
            raise ValueError(
                f"Product {product.get('id', '<unknown>')} missing fields: {missing}"
            )


def normalize_price(price_text: str) -> Optional[float]:
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
