"""
E-Commerce Product Tracker — Tkinter GUI

English UI that mirrors the CLI functionality in `ecommerce_tracker.py`.
Run: python3 ecommerce_gui.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List

# Import logic and dataset from the CLI module to avoid duplication
from ecommerce_tracker import (
    PRODUCTS,
    sanitize_buyer_id,
    validate_name,
    average_price,
    find_products_by_keyword,
    show_product_slices,
)


class EcommerceGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("E-Commerce Product Tracker")
        self.geometry("780x520")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        # Input frame
        frm_inputs = ttk.LabelFrame(self, text="Buyer & Search Inputs")
        frm_inputs.place(x=10, y=10, width=460, height=220)

        labels = ["Buyer name:", "Buyer ID:", "Email:", "Search keyword:"]
        self.entries = {}
        for i, lbl in enumerate(labels):
            ttk.Label(frm_inputs, text=lbl).grid(row=i, column=0, sticky="w", padx=8, pady=4)
            ent = ttk.Entry(frm_inputs, width=36)
            ent.grid(row=i, column=1, padx=8, pady=4)
            self.entries[lbl] = ent

        # Action buttons
        btn_frame = ttk.Frame(self)
        btn_frame.place(x=10, y=240, width=460, height=60)
        ttk.Button(btn_frame, text="Search / Analyze", command=self.on_search).pack(side="left", padx=8, pady=8)
        ttk.Button(btn_frame, text="Clear", command=self.on_clear).pack(side="left", padx=8)
        ttk.Button(btn_frame, text="Dataset summary", command=self.show_dataset_summary).pack(side="left", padx=8)

        # Results frame
        frm_results = ttk.LabelFrame(self, text="Results & Matches")
        frm_results.place(x=480, y=10, width=290, height=400)

        self.txt_results = tk.Text(frm_results, width=36, height=20, wrap="word")
        self.txt_results.pack(padx=6, pady=6)

        # Matches and confirmation
        frm_matches = ttk.LabelFrame(self, text="Matches / Confirm")
        frm_matches.place(x=10, y=310, width=460, height=200)

        self.lst_matches = tk.Listbox(frm_matches, height=6, width=56)
        self.lst_matches.pack(side="left", padx=6, pady=6)
        self.lst_matches.bind("<<ListboxSelect>>", self.on_select_match)

        scrollbar = ttk.Scrollbar(frm_matches, orient="vertical", command=self.lst_matches.yview)
        scrollbar.pack(side="left", fill="y")
        self.lst_matches.config(yscrollcommand=scrollbar.set)

        right_col = ttk.Frame(frm_matches)
        right_col.pack(side="left", padx=6)
        ttk.Button(right_col, text="Confirm Selected", command=self.on_confirm).pack(pady=6)
        self.lbl_validation = ttk.Label(right_col, text="Validations:")
        self.lbl_validation.pack()

        # Status bar
        self.status = ttk.Label(self, text="Ready", relief="sunken", anchor="w")
        self.status.place(x=0, y=500, relwidth=1)

    def on_search(self):
        # Read inputs and trim
        buyer_name = self.entries["Buyer name:"].get().strip()
        buyer_id_raw = self.entries["Buyer ID:"].get().strip()
        email_raw = self.entries["Email:"].get().strip()
        keyword = self.entries["Search keyword:"].get().strip()

        # Basic processing
        name_len = len(buyer_name)
        id_len = len(buyer_id_raw)
        first_letter = None
        letter_count = None
        if keyword:
            first_letter = keyword[0].lower()
            letter_count = keyword.lower().count(first_letter)

        name_is_alpha = validate_name(buyer_name)
        id_is_alnum = buyer_id_raw.isalnum()

        email = email_raw.lower()
        email_username = email.split("@")[0] if "@" in email else email

        buyer_id_sanitized = sanitize_buyer_id(buyer_id_raw)
        buyer_id_reversed = buyer_id_sanitized[::-1]

        # Find matching products
        matches = find_products_by_keyword(PRODUCTS, keyword)

        # Display validations and slices in results text
        self.txt_results.delete("1.0", tk.END)
        self.txt_results.insert(tk.END, f"Name (trimmed): '{buyer_name}' | length: {name_len}\n")
        self.txt_results.insert(tk.END, f"isalpha (spaces removed): {name_is_alpha}\n")
        self.txt_results.insert(tk.END, f"Buyer ID (raw): '{buyer_id_raw}' | length: {id_len} | isalnum: {id_is_alnum}\n")
        self.txt_results.insert(tk.END, f"Buyer ID (sanitized): '{buyer_id_sanitized}' | reversed: '{buyer_id_reversed}'\n")
        self.txt_results.insert(tk.END, f"Email (lowercased): '{email}' | username slice: '{email_username}'\n")
        if first_letter is not None:
            self.txt_results.insert(tk.END, f"Letter '{first_letter}' occurs {letter_count} times in keyword '{keyword}' (case-insensitive, using first character)\n")

        # Show matches in listbox
        self.lst_matches.delete(0, tk.END)
        if matches:
            for p in matches:
                self.lst_matches.insert(tk.END, f"{p['name']} ({p['category']}) - ${p['price']:.2f}")
            self.status.config(text=f"Found {len(matches)} matches")
        else:
            self.status.config(text="No matches found")

    def on_select_match(self, event):
        sel = self.lst_matches.curselection()
        if not sel:
            return
        idx = sel[0]
        text = self.lst_matches.get(idx)
        # show more details in results
        # derive product by name
        prod_name = text.split(" (")[0]
        prod = next((p for p in PRODUCTS if p['name'] == prod_name), None)
        if prod:
            self.txt_results.insert(tk.END, "\n--- Selected product ---\n")
            self.txt_results.insert(tk.END, f"Name: {prod['name']}\n")
            self.txt_results.insert(tk.END, f"Category: {prod['category']}\n")
            self.txt_results.insert(tk.END, f"Price: ${prod['price']:.2f}\n")
            self.txt_results.insert(tk.END, show_product_slices(prod) + "\n")

    def on_confirm(self):
        sel = self.lst_matches.curselection()
        if not sel:
            messagebox.showinfo("Confirm", "No product selected to confirm.")
            return
        idx = sel[0]
        selection_text = self.lst_matches.get(idx)
        prod_name = selection_text.split(" (")[0]
        prod = next((p for p in PRODUCTS if p['name'] == prod_name), None)
        if not prod:
            messagebox.showinfo("Confirm", "Could not find product details.")
            return

        buyer_name = self.entries["Buyer name:"].get().strip()
        buyer_id_sanitized = sanitize_buyer_id(self.entries["Buyer ID:"].get().strip())
        email = self.entries["Email:"].get().strip().lower()

        # Format confirmations in two ways
        conf_f = f"Request: Buyer {buyer_name} (ID {buyer_id_sanitized}) requested '{prod['name']}' at ${prod['price']:.2f}."
        conf_format = "Request: Buyer {0} <{1}> requested '{2}' priced at ${3:.2f}.".format(buyer_name, email, prod['name'], prod['price'])

        # Ask final confirmation
        if messagebox.askyesno("Confirm Request", conf_f + "\n\nConfirm?"):
            messagebox.showinfo("Confirmed", "✅ Confirmation sent:\n" + conf_format)
            self.status.config(text=f"Confirmed request for {prod['name']}")
        else:
            self.status.config(text="Request not confirmed")

    def on_add_to_cart(self):
        sel = self.lst_matches.curselection()
        if not sel:
            messagebox.showinfo("Add to cart", "No product selected to add.")
            return
        idx = sel[0]
        selection_text = self.lst_matches.get(idx)
        prod_name = selection_text.split(" (")[0]
        prod = next((p for p in PRODUCTS if p['name'] == prod_name), None)
        if not prod:
            messagebox.showinfo("Add to cart", "Could not find product details.")
            return
        self.cart.append(prod)
        self.status.config(text=f"Added {prod['name']} to cart")

    def on_view_cart(self):
        msg = cart_summary(self.cart)
        messagebox.showinfo("Cart contents", msg)

    def on_clear_cart(self):
        self.cart.clear()
        self.status.config(text="Cart cleared")

    def on_clear(self):
        for ent in self.entries.values():
            ent.delete(0, tk.END)
        self.txt_results.delete("1.0", tk.END)
        self.lst_matches.delete(0, tk.END)
        self.status.config(text="Cleared inputs")

    def show_dataset_summary(self):
        avg = average_price(PRODUCTS)
        names = tuple(p['name'] for p in PRODUCTS)
        cats = set(p['category'] for p in PRODUCTS)
        msg = f"Products: {len(PRODUCTS)} | Average price: ${avg:.2f}\nNames: {names}\nCategories: {cats}"
        messagebox.showinfo("Dataset summary", msg)


if __name__ == "__main__":
    app = EcommerceGUI()
    app.mainloop()
