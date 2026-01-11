from playwright.async_api import async_playwright

async def fetch_price(url: str, price_selector : str)-> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")

         # Wait for price element to appear
        await page.wait_for_selector(price_selector, timeout=15000)
        price_text = await page.locator(price_selector).inner_text()

        await browser.close()
        return price_text.strip()
        