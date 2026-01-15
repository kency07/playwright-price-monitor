import asyncio
from src.scraper import fetch_price
from src.utils import normlized_price
from src.monitor import check_price
from src.notifier import notify

# Example values — replace with real product details locally

product_id = "example_product_123"
url = "https://example.com/product/123"
price_selector = ".price"


CHECK_INTERVAL = 60 # testing

async def montior():
    while True:
        try:
            raw_price = await fetch_price(url, price_selector)
            current_price = normlized_price(raw_price)
        
            last_price, status = check_price(product_id, current_price)

            notify(f"[CHECK] current price: {current_price}")

            if status == "price_dropped":
                notify(
                    f" 📉 PRICE DROPPED from {last_price} -> {current_price}",
                    email=True
                       )
            elif status == "price_increased":
                notify(
                    f"📈 PRICE INCREASED from {last_price} -> {current_price}",
                    email=True
                    )    
            elif status == "first_check":
                 notify("FIRST price recorded ")
            
               

        except Exception as e:
            notify(f"⚠ Error : {e}")
        await asyncio.sleep(CHECK_INTERVAL)

asyncio.run(montior())