"""
E-Commerce Product Tracker — Streamlit Web UI

Run:
    pip install streamlit
    streamlit run ecommerce_streamlit.py

This mirrors the CLI/Tkinter functionality but opens in the browser (no X server needed).
"""

from typing import List, Dict

try:
    import streamlit as st
except Exception as e:
    raise SystemExit(
        "Streamlit is required to run this app. Install with: pip install streamlit"
    )

from ecommerce_tracker import (
    PRODUCTS,
    sanitize_buyer_id,
    validate_name,
    average_price,
    find_products_by_keyword,
    show_product_slices,
    add_to_cart,
    remove_from_cart,
    cart_total,
    cart_summary,
)

# Initialize cart in session state
if 'cart' not in st.session_state:
    st.session_state['cart'] = []


st.set_page_config(page_title="E-Commerce Product Tracker", layout="wide")

st.title("E-Commerce Product Tracker")
st.markdown("Track items and confirm a buyer request (English UI).")

with st.sidebar:
    st.header("Inputs")
    buyer_name = st.text_input("Buyer name")
    buyer_id_raw = st.text_input("Buyer ID")
    email_raw = st.text_input("Email")
    keyword = st.text_input("Search keyword")

st.sidebar.markdown("---")
if st.sidebar.button("Analyze / Search"):
    # Basic processing
    buyer_name_trimmed = buyer_name.strip()
    buyer_id_trimmed = buyer_id_raw.strip()
    name_len = len(buyer_name_trimmed)
    id_len = len(buyer_id_trimmed)
    first_letter = None
    letter_count = None
    if keyword:
        first_letter = keyword[0].lower()
        letter_count = keyword.lower().count(first_letter)

    name_is_alpha = validate_name(buyer_name_trimmed)
    id_is_alnum = buyer_id_trimmed.isalnum()

    email = email_raw.strip().lower()
    email_username = email.split("@")[0] if "@" in email else email

    buyer_id_sanitized = sanitize_buyer_id(buyer_id_trimmed)
    buyer_id_reversed = buyer_id_sanitized[::-1]

    # Find matches
    matches = find_products_by_keyword(PRODUCTS, keyword)

    # Display results
    st.subheader("Input analysis")
    st.write(f"Name (trimmed): '{buyer_name_trimmed}' | length: {name_len} | isalpha (spaces removed): {name_is_alpha}")
    st.write(f"Buyer ID (raw): '{buyer_id_trimmed}' | length: {id_len} | isalnum: {id_is_alnum}")
    st.write(f"Buyer ID (sanitized): '{buyer_id_sanitized}' | reversed: '{buyer_id_reversed}'")
    st.write(f"Email (lowercased): '{email}' | username slice: '{email_username}'")
    if first_letter is not None:
        st.write(f"Letter '{first_letter}' occurs {letter_count} times in keyword '{keyword}' (case-insensitive, using first character)")

    st.subheader("Product matches")
    if matches:
        # show as a table
        st.table([
            {"name": p["name"], "category": p["category"], "price": f"${p['price']:.2f}"}
            for p in matches
        ])

        # show find() / rfind() and slices and Add-to-cart buttons
        for p in matches:
            pos_first = p["name"].lower().find(keyword.lower()) if keyword else -1
            pos_last = p["name"].lower().rfind(keyword.lower()) if keyword else -1
            st.write(show_product_slices(p) + f" | first found at {pos_first}, last found at {pos_last}")
            if st.button("Add to cart", key=f"add_{p['name']}"):
                # add a shallow copy to avoid accidental mutation
                st.session_state['cart'].append(p)
                st.success(f"Added '{p['name']}' to cart")

        # selection and confirmation
        names = [p["name"] for p in matches]
        selected = st.selectbox("Select product to confirm", options=names)
        chosen = next((p for p in matches if p["name"] == selected), None)

        if chosen:
            st.markdown("---")
            conf_f = f"Request: Buyer {buyer_name_trimmed} (ID {buyer_id_sanitized}) requested '{chosen['name']}' at ${chosen['price']:.2f}."
            conf_format = "Request: Buyer {0} <{1}> requested '{2}' priced at ${3:.2f}.".format(buyer_name_trimmed, email, chosen['name'], chosen['price'])
            st.write("**Using f-string:**")
            st.write(conf_f)
            st.write("**Using .format():**")
            st.write(conf_format)

            if st.button("Confirm request"):
                st.success("✅ Confirmation sent: " + conf_f)
    else:
        st.info("No matches found for the given keyword.")

# Cart in sidebar
st.sidebar.markdown("---")
st.sidebar.header("Cart")
if st.session_state['cart']:
    for i, it in enumerate(st.session_state['cart'], start=1):
        st.sidebar.write(f"{i}. {it['name']} ({it['category']}) - ${it['price']:.2f}")
    total = cart_total(st.session_state['cart'])
    st.sidebar.write(f"**Total ({len(st.session_state['cart'])} items):** ${total:.2f}")
    if st.sidebar.button("Checkout"):
        st.success("✅ Checkout complete:\n" + cart_summary(st.session_state['cart']))
        st.session_state['cart'].clear()
    if st.sidebar.button("Clear cart"):
        st.session_state['cart'].clear()
        st.sidebar.info("Cart cleared")
else:
    st.sidebar.info("Cart is empty")

# Dataset summary column
st.sidebar.markdown("---")
if st.sidebar.button("Show dataset summary"):
    avg = average_price(PRODUCTS)
    names = tuple(p["name"] for p in PRODUCTS)
    cats = set(p["category"] for p in PRODUCTS)
    st.sidebar.write(f"Products: {len(PRODUCTS)} | Average price: ${avg:.2f}")
    st.sidebar.write(f"Names: {names}")
    st.sidebar.write(f"Categories: {cats}")

# Show full product list on main page
st.header("Available products")
for p in PRODUCTS:
    st.write(f"- {p['name']} ({p['category']}) - ${p['price']:.2f}")
    if st.button("Add to cart", key=f"add_all_{p['name']}"):
        st.session_state['cart'].append(p)
        st.success(f"Added '{p['name']}' to cart")
