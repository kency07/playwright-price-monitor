import re

def normlized_price (price_text: str)->float:
    """
    Extract numeric price from strings like:
    ₹8,299 | $12.5 | €13 | 123 | 23.0
    """
    # case 1: invalid or empty
    if not isinstance(price_text, str):
        return None
     # Remove currency symbols and spaces
    # case2: string price
    price_text = price_text.replace(",", "")
    match = re.search(r"\d+(?:\.\d+)?",   price_text)
    #Handle comma as thousand separator
    

    return float(match.group()) if match else None