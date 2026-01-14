"""
E-Commerce Product Tracker

Brief: Track items and confirm a buyer request.
Dataset: 5 products (name, category, price).
User inputs: buyer name, buyer ID, email, search keyword.

This script demonstrates various string methods, validations, slicing,
and use of Python data structures as requested.
"""

from typing import List, Dict, Tuple, Set

PRODUCTS: List[Dict[str, object]] = [
    {"name": "Wireless Earbuds", "category": "Electronics", "price": 59.99},
    {"name": "Yoga Mat", "category": "Sports", "price": 24.50},
    {"name": "Stainless Water Bottle", "category": "Outdoor", "price": 19.95},
    {"name": "Bluetooth Speaker", "category": "Electronics", "price": 89.99},
    {"name": "Smart LED Bulb", "category": "Home", "price": 12.99},
]

FORBIDDEN_IN_ID = [" ", "-", ".", "#"]


def sanitize_buyer_id(bid: str) -> str:
    """Replace forbidden characters in buyer ID using str.replace()."""
    s = bid
    for ch in FORBIDDEN_IN_ID:
        s = s.replace(ch, "")
    return s


def validate_name(name: str) -> bool:
    """Check that name (with spaces removed) contains only letters."""
    return name.replace(" ", "").isalpha()


def average_price(products: List[Dict[str, object]]) -> float:
    return sum(p["price"] for p in products) / len(products)


def product_names_tuple(products: List[Dict[str, object]]) -> Tuple[str, ...]:
    return tuple(p["name"] for p in products)


def unique_categories(products: List[Dict[str, object]]) -> Set[str]:
    return set(p["category"] for p in products)


def find_products_by_keyword(products: List[Dict[str, object]], kw: str) -> List[Dict[str, object]]:
    kw_low = kw.lower()
    matches = []
    for p in products:
        name_low = p["name"].lower()
        if kw_low in name_low:
            matches.append(p)
    return matches


def show_product_slices(p: Dict[str, object]) -> str:
    name = p["name"]
    first3 = name[:3]
    last3 = name[-3:]
    return f"'{name}' -> first3: '{first3}', last3: '{last3}'"

def add_to_cart(cart: List[Dict[str, object]], product: Dict[str, object]) -> None:
    """Append a product to the cart (list of product dicts)."""
    cart.append(product)


def remove_from_cart(cart: List[Dict[str, object]], product_name: str) -> None:
    """Remove the first occurrence of a product with the given name from the cart."""
    for i, p in enumerate(cart):
        if p["name"] == product_name:
            cart.pop(i)
            return


def cart_total(cart: List[Dict[str, object]]) -> float:
    """Return total price of items in the cart."""
    return sum(p["price"] for p in cart)


def cart_summary(cart: List[Dict[str, object]]) -> str:
    """Return a human-readable summary of cart contents and total."""
    if not cart:
        return "Cart is empty."
    lines = [f"- {p['name']} ({p['category']}) - ${p['price']:.2f}" for p in cart]
    total = cart_total(cart)
    return "\n".join(lines) + f"\n\nTotal ({len(cart)} items): ${total:.2f}"

def summary(products: List[Dict[str, object]]) -> str:
    avg = average_price(products)
    names = product_names_tuple(products)
    cats = unique_categories(products)

    return (
        f"Products: {len(products)} | Average price: ${avg:.2f}\n"
        f"Names (tuple): {names}\n"
        f"Categories (set): {cats}"
    )


def interactive():
    print("\nE-Commerce Product Tracker — interactive demo")
    print("(Enter values when prompted — type 'exit' at buyer name to quit)\n")

    # Show dataset summary
    print("Dataset summary:")
    print(summary(PRODUCTS))
    print("\nAvailable products:")
    for idx, p in enumerate(PRODUCTS, start=1):
        print(f" {idx}. {p['name']} ({p['category']}) - ${p['price']:.2f}")
    print()

    # Collect inputs
    buyer_name = input("Buyer name: ").strip()
    if buyer_name.lower() in ("exit", "quit"):
        print("Exiting.")
        return

    buyer_id_raw = input("Buyer ID: ").strip()
    email_raw = input("Email: ").strip()
    keyword_raw = input("Search keyword: ").strip()

    # Processing: trimming, lengths, counts
    buyer_name_trimmed = buyer_name  # already stripped
    buyer_id_trimmed = buyer_id_raw
    keyword = keyword_raw

    name_len = len(buyer_name_trimmed)
    id_len = len(buyer_id_trimmed)

    # count occurrences of the first letter of the keyword (case-insensitive)
    letter_count_in_keyword = None
    first_letter = None
    if keyword:
        first_letter = keyword[0].lower()
        letter_count_in_keyword = keyword.lower().count(first_letter)

    # Validations
    name_is_alpha = validate_name(buyer_name_trimmed)
    id_is_alnum = buyer_id_trimmed.isalnum()

    # Email normalization and slicing
    email = email_raw.lower()
    if "@" in email:
        email_username = email.split("@")[0]
    else:
        email_username = email  # fallback if no @ present

    # Replace forbidden chars in ID and reverse
    buyer_id_sanitized = sanitize_buyer_id(buyer_id_trimmed)
    buyer_id_reversed = buyer_id_sanitized[::-1]

    # Data structures
    avg_price = average_price(PRODUCTS)
    buyer_record = {
        "name": buyer_name_trimmed,
        "id": buyer_id_sanitized,
        "email": email,
    }
    product_names = product_names_tuple(PRODUCTS)
    categories = unique_categories(PRODUCTS)

    # Search
    matches = find_products_by_keyword(PRODUCTS, keyword)

    # Output results
    print("\n--- INPUT ANALYSIS ---")
    print(f"Name (trimmed): '{buyer_name_trimmed}' | length: {name_len} | isalpha (spaces removed): {name_is_alpha}")
    print(f"Buyer ID (raw): '{buyer_id_trimmed}' | length: {id_len} | isalnum: {id_is_alnum}")
    print(f"Buyer ID (sanitized): '{buyer_id_sanitized}' | reversed: '{buyer_id_reversed}'")
    print(f"Email (lowercased): '{email}' | username slice: '{email_username}'")

    if first_letter is not None:
        print(f"Letter '{first_letter}' occurs {letter_count_in_keyword} times in keyword '{keyword}' (case-insensitive, using first character of keyword)")

    print("\n--- PRODUCTS MATCHING KEYWORD ---")
    if matches:
        for i, p in enumerate(matches, start=1):
            # demonstrate find() and rfind()
            name_low = p['name'].lower()
            pos_first = name_low.find(keyword.lower())
            pos_last = name_low.rfind(keyword.lower())
            slices = show_product_slices(p)
            print(f" {i}. {p['name']} - first found at {pos_first}, last found at {pos_last}. {slices}")
    else:
        print(" No matches found.")

    # Show some data structures
    print("\n--- DATA STRUCTURES ---")
    print(f"Average price of products: ${avg_price:.2f}")
    print(f"Buyer record (dict): {buyer_record}")
    print(f"Product names (tuple): {product_names}")
    print(f"Unique categories (set): {categories}")

    # Formatting confirmation: using f-string and .format()
    if matches:
        chosen = matches[0]
        # f-string
        conf_f = f"Request: Buyer {buyer_record['name']} (ID {buyer_record['id']}) requested '{chosen['name']}' at ${chosen['price']:.2f}."
        # .format()
        conf_format = "Request: Buyer {0} <{1}> requested '{2}' priced at ${3:.2f}.".format(
            buyer_record['name'], buyer_record['email'], chosen['name'], chosen['price']
        )

        print("\n--- CONFIRMATIONS ---")
        print("Using f-string: ")
        print(conf_f)
        print("Using .format(): ")
        print(conf_format)

        # Ask to confirm request
        confirm = input("\nConfirm request for the first matched product? (y/n): ").strip().lower()
        if confirm == 'y':
            print(f"\n✅ Confirmation sent: {buyer_record['name']} -> {chosen['name']}")
        else:
            print("\nRequest not confirmed.")
    else:
        print("No product to confirm.")


if __name__ == '__main__':
    interactive()
