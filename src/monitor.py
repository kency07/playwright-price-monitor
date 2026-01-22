import json
from pathlib import Path
import logging
from typing import Optional

DATA_FILE = Path("data/prices.json")


def load_prices():
    if not DATA_FILE.exists():
        return {}
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logging.warning(f"{DATA_FILE} is corrupted, backing it up")
        # backup corrupted file
        try:
            DATA_FILE.rename(DATA_FILE.with_suffix(".corrupted.json"))
        except Exception:
            logging.exception("Failed to rename corrupted price file")
        return {}
    except Exception:
        logging.exception("Failed to load prices file")
        return {}


def save_prices(data):
    try:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception:
        logging.exception("Failed to save prices")


def check_price(product_id: str, current_price: float)->{Optional[float], str} :
    prices = load_prices()
    last_price = prices.get(product_id)

    if last_price is None:
        prices[product_id] = current_price
        save_prices(prices)
        return None, "first_check"

    if current_price < last_price:
        status = "price_dropped"
    elif current_price > last_price:
        status = "price_increased"
    else:
        status = "no_change"

    prices[product_id] = current_price
    save_prices(prices)

    return last_price, status
