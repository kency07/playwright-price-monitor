 #code in this file is only used in  v1.4 — implement multi-product monitoring and core refactor
# so ignore it and use products.json only
PRODUCTS = [
    {
        "id": "PLACEHOLDER_ID_1",
        "url": "PLACEHOLDER_URL_1",
        "price_selector": "PLACEHOLDER_PRICE_SELECTOR_1"
    },
    {
        "id": "PLACEHOLDER_ID_2",
        "url": "PLACEHOLDER_URL_2",
        "price_selector": "PLACEHOLDER_PRICE_SELECTOR_2"
    }
]

ids = [p["id"] for p in PRODUCTS]
if  len(ids) != len(set(ids)):      
    """assert can silently disappear  When Python runs with -O (capital letter O) is Python optimize flag"""
    raise RuntimeError( "Duplicate product IDs detected!")
    
CHECK_INTERVAL = 60  # testing
