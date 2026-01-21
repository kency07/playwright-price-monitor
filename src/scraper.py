from playwright.async_api import TimeoutError as playwrightTimeout
import logging
from typing import Optional


async def fetch_price_with_browser(
    browser, url: str, price_selector: str
) -> Optional[str]:

    page = await browser.new_page()
    try:

        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_selector(price_selector, timeout=15000)
        # Wait for price element to appear
        price_text = await page.locator(price_selector).inner_text()
        return price_text.strip()
    except playwrightTimeout:
        logging.warning("playwright timeout while loading %s", url)
        return None
    except Exception:
        logging.exception("Unexpected playwright Error")
        return None
    finally:
        try:
            await page.close()
        except Exception:
            logging.exception("failed to close Playwright page")
