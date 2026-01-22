from contextlib import asynccontextmanager
from playwright.async_api import async_playwright
import asyncio
import logging


@asynccontextmanager
async def browser_manager(headless: bool = True):
    """
    Async context manager to start Playwright browser and close it automatically.
    """

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        try:
            yield browser
        finally:
            try:
                await browser.close()  # ensures cleanup even on exceptions
            except asyncio.CancelledError:
                pass   # intentional: suppress Ctrl+C noise during shutdown

            except Exception:
                logging.exception("Failed to close Playwright browser")
