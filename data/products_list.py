PRODUCTS = [
    {
        "id": "PLACEHOLDER_ID_1",
        "url": "PLACEHOLDER_URL_1",
        "price_selector": "PLACEHOLDER_PRICE_SELECTOR_1",
    },
    {
        "id": "PLACEHOLDER_ID_2",
        "url": "PLACEHOLDER_URL_2",
        "price_selector": "PLACEHOLDER_PRICE_SELECTOR_2",
    },
]

ids = [p["id"] for p in PRODUCTS]
assert len(ids) == len(set(ids)), "Duplicate product IDs detected!"
CHECK_INTERVAL = 60  # testing
