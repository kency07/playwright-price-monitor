from logging_config import setup_logging

setup_logging()
import asyncio
from data.products_list import PRODUCTS, CHECK_INTERVAL
from src.browser_manager import browser_manager
from src.scraper import fetch_price_with_browser
from src.utils import normalized_price, is_connected
from src.monitor import check_price
from src.notifier import notify, email_manager
import logging

sem = asyncio.Semaphore(5)  # Only 5 concurrent browser pages at a time


async def monitor_product(browser, product):

    while True:
        try:
            async with sem:
                raw_price = await fetch_price_with_browser(
                    browser, product["url"], product["price_selector"]
                )
            if raw_price is None:
                logging.warning(f"{product['id']} price not found, skipping")
                await asyncio.sleep(CHECK_INTERVAL)
                continue

            current_price = normalized_price(raw_price)

            if current_price is None:
                logging.warning(f"{product['id']} price could not be normalized, skipping")
                await asyncio.sleep(CHECK_INTERVAL)
                continue

            last_price, status = check_price(product["id"], current_price)

            notify(f"[CHECK] current price: {current_price}")

            if status == "price_dropped":
                notify(
                    f" 📉 PRICE DROPPED from {last_price} -> {current_price}\n{product['url']}",
                    email=True,
                )
            elif status == "price_increased":
                notify(
                    f"📈 PRICE INCREASED from {last_price} -> {current_price}\n{product['url']}",
                    email=True,
                )
            elif status == "first_check":
                notify(f"{product['id']} FIRST price recorded ")

        except asyncio.CancelledError:
            notify(f" Monitoring for {product['id']} stopped.")
            raise
        except Exception:
            logging.exception(f" {product['id']} crashed")

        await asyncio.sleep(CHECK_INTERVAL)


async def main():

    is_connected()

    async with browser_manager() as browser:
        task = [
            asyncio.create_task(monitor_product(browser, product))
            for product in PRODUCTS
        ]
        task.append(asyncio.create_task(email_manager()))
        try:
            await asyncio.gather(*task)

        except asyncio.CancelledError:
            # Cancel all running monitoring tasks
            for t in task:
                t.cancel()
            await asyncio.gather(*task, return_exceptions= True)
            logging.info("All monitoring tasks cancelled.")


if __name__ == "__main__":

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("monitoring stopped by user")
