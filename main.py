import streamlit as st
import pandas as pd
import os

# --- Page Config ---
st.set_page_config(page_title="Restaurant App", page_icon="🍔")

# CSV File for data persistence
DATA_FILE = 'menu_data.csv'

# Initialize default menu if file doesn't exist
def load_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "Item": ["Beef Burger", "Chicken Pizza", "Fries", "Coke"],
            "Category": ["Mains", "Mains", "Sides", "Drinks"],
            "Price": [120.0, 150.0, 45.0, 20.0]
        }
        df = pd.DataFrame(default_data)
        df.to_csv(DATA_FILE, index=False)
        return df
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Session state for cart
if 'cart' not in st.session_state:
    st.session_state.cart = []

df_menu = load_data()

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Take Order", "Manage Menu", "View Cart"])

# --- Page 1: Take Order ---
if page == "Take Order":
    st.header("🍽️ Menu & Order")
    
    # Filter by category
    cats = ["All"] + list(df_menu["Category"].unique())
    selected_cat = st.selectbox("Filter by Category", cats)
    
    if selected_cat != "All":
        filtered_df = df_menu[df_menu["Category"] == selected_cat]
    else:
        filtered_df = df_menu
        
    st.table(filtered_df)
    
    st.divider()
    st.subheader("Add to Cart")
    
    col1, col2 = st.columns(2)
    with col1:
        item_choice = st.selectbox("Select Item", df_menu["Item"].values)
    with col2:
        qty = st.number_input("Quantity", min_value=1, value=1, step=1)
        
    if st.button("Add Item"):
        price = df_menu[df_menu["Item"] == item_choice]["Price"].values[0]
        st.session_state.cart.append({
            "Item": item_choice,
            "Price": price,
            "Qty": qty,
            "Total": price * qty
        })
        st.success(f"Added {qty}x {item_choice} to cart!")

# --- Page 2: Manage Menu (Admin) ---
elif page == "Manage Menu":
    st.header("⚙️ Admin Panel")
    
    st.subheader("Current Menu")
    st.table(df_menu)
    st.subheader("Add New Item")
    with st.form("add_item_form"):
        new_name = st.text_input("Item Name")
        new_cat = st.text_input("Category")
        new_price = st.number_input("Price (EGP)", min_value=0.0, step=5.0)
        
        submit = st.form_submit_button("Save Item")
        
        if submit:
            if new_name and new_cat:
                new_row = pd.DataFrame([{"Item": new_name, "Category": new_cat, "Price": new_price}])
                df_menu = pd.concat([df_menu, new_row], ignore_index=False)
                save_data(df_menu)
                st.success("Item added successfully! Please refresh.")
            else:
                st.error("Please fill all fields.")

# --- Page 3: View Cart & Checkout ---
elif page == "View Cart":
    st.header("🛒 Cart & Bill")
    
    if len(st.session_state.cart) == 0:
        st.info("Your cart is empty.")
    else:
        cart_df = pd.DataFrame(st.session_state.cart)
        st.table(cart_df)
        
        grand_total = cart_df["Total"].sum()
        st.subheader(f"Total Amount: {grand_total:.2f} EGP")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Checkout / Print Receipt"):
                st.balloons()
                st.success("Order Placed Successfully!")
                st.session_state.cart = [] # Clear cart
        with c2:
            if st.button("Clear Cart"):
                st.session_state.cart = []
                st.rerun()