from playwright.async_api import TimeoutError as PlaywrightTimeoutError
import logging
from typing import Optional


async def fetch_price_with_browser(
    browser, url: str, price_selector: str
) -> Optional[str]:

    page = await browser.new_page()
    try:
        try:  # Page load timeout → network / site issue
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        except PlaywrightTimeoutError:
            logging.warning("playwright timeout while loading %s", url)
            return None
        try:
            # Selector timeout → selector/config issue
            await page.wait_for_selector(price_selector, timeout=15000)
        except PlaywrightTimeoutError:
            logging.error(
                "Price selector not found (likely wrong selector): %s, %s",
                price_selector,
                url,
            )
            return None
        # Wait for price element to appear
        price_text = await page.locator(price_selector).inner_text()
        return price_text.strip()
    except Exception:
        # Truly unexpected bugs
        logging.exception("Unexpected playwright Error while fetching price")
        raise
    finally:
        try:
            await page.close()
        except Exception:
            logging.exception("failed to close Playwright page")
