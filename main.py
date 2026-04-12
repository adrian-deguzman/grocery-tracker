import streamlit as st

# --- Page Config (Makes it look nice on mobile) ---
st.set_page_config(page_title="Grocery Tracker", page_icon="🛒", layout="centered")
st.title("🛒 My Grocery Tracker")

# --- Initialize Memory ---
if "cart" not in st.session_state:
    st.session_state.cart = []
    
# We use this counter to forcefully clear the "Add Item" inputs
if "form_key" not in st.session_state:
    st.session_state.form_key = 0

# --- Pre-Calculate Math ---
total_sum = sum(item["price"] * item["qty"] for item in st.session_state.cart if item["selected"])

# --- Requirement 4 Update: Pin Total at Top (Sticky CSS) ---
pin_total = st.toggle("📌 Pin Total at Top", value=False)

# --- Mobile Optimization CSS & Pinned Total Banner ---
st.markdown(
    f"""
    <style>
        /* Sticky Total CSS */
        .pinned-total {{
            position: fixed;
            top: 55px; /* Sits safely below the mobile Streamlit menu bar */
            left: 0;
            right: 0;
            background-color: #2e7d32; /* High-visibility green */
            color: white;
            padding: 12px;
            text-align: center;
            font-size: 20px;
            font-weight: bold;
            z-index: 99999; /* Ensures it stays above all other elements */
            box-shadow: 0px 4px 6px rgba(0,0,0,0.3);
        }}
        /* Add padding to the main container so the banner doesn't hide the top items */
        .block-container {{
            padding-top: {"80px" if pin_total else "2rem"};
        }}
        
        /* Force ONLY the Shopping List rows (Checkbox + Item Popover) to stay perfectly grouped */
        div[data-testid="stHorizontalBlock"]:has(.stCheckbox) {{
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            gap: 8px !important; /* Force a small, precise gap between checkbox and button */
        }}
        /* HARDCODE the checkbox column to exactly 40px so it cannot stretch and push the button */
        div[data-testid="stHorizontalBlock"]:has(.stCheckbox) > div[data-testid="column"]:nth-child(1) {{
            width: 40px !important; 
            min-width: 40px !important;
            max-width: 40px !important;
            flex: 0 0 40px !important; 
        }}
        /* Tell the button column to dynamically fill whatever space is left over */
        div[data-testid="stHorizontalBlock"]:has(.stCheckbox) > div[data-testid="column"]:nth-child(2) {{
            width: calc(100% - 48px) !important; 
            flex: 1 1 calc(100% - 48px) !important; 
            min-width: 0 !important;
        }}
        
        /* Left-align text inside the popover buttons so it looks like a list, not a centered button */
        button[data-testid="stPopoverButton"] {{
            justify-content: flex-start !important;
            text-align: left !important;
            padding-left: 10px !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

if pin_total:
    st.markdown(f'<div class="pinned-total">Grand Total: ₱{total_sum:.2f}</div>', unsafe_allow_html=True)

# --- Add New Item Section ---
with st.expander("➕ Add New Item", expanded=True):
    col1, col2 = st.columns(2)
    
    fk = st.session_state.form_key # Get the current key counter
    
    with col1:
        item_name = st.text_input("Item Name", key=f"name_{fk}")
        item_price = st.number_input("Price per piece", min_value=0.0, step=0.50, value=None, placeholder="", key=f"price_{fk}")
    
    with col2:
        item_qty = st.number_input("Quantity", min_value=1, step=1, key=f"qty_{fk}")
        item_image = st.file_uploader("Upload or Take Picture", type=["jpg", "png", "jpeg"], key=f"img_{fk}")

    if st.button("Add to Cart", type="primary"):
        if item_name:
            new_item = {
                "name": item_name,
                "price": item_price if item_price is not None else 0.0,
                "qty": item_qty,
                "image": item_image,
                "selected": True 
            }
            st.session_state.cart.append(new_item)
            st.toast(f"Added {item_name}!", icon="🛒")
            st.session_state.form_key += 1 # Clears the inputs
            st.rerun()
        else:
            st.error("Please give the item a name!")

# --- List Items, Toggles, and Editing ---
st.header("🧾 Your List")

if not st.session_state.cart:
    st.info("Your cart is empty. Add something above!")
else:
    # Loop through our saved items
    for i, item in enumerate(st.session_state.cart):
        
        # Place the Checkbox and Clickable Details side-by-side
        # (The columns array [1, 8] doesn't matter much here because our custom CSS overrides it!)
        col_check, col_details = st.columns([1, 8], vertical_alignment="center")
        
        with col_check:
            is_checked = st.checkbox(
                f"Select {item['name']}", # Hidden string for accessibility 
                value=item["selected"], 
                key=f"check_{i}",
                label_visibility="collapsed"
            )
            
            # Instantly update state if clicked
            if is_checked != item["selected"]:
                st.session_state.cart[i]["selected"] = is_checked
                st.rerun()
        
        with col_details:
            # We use the item name and price as the label for the popover!
            # This makes the entire text a clickable button that opens the edit menu.
            button_label = f"{item['name']}  |  {item['qty']} x ₱{item['price']:.2f}"
            
            with st.popover(button_label, use_container_width=True):
                
                # Placed Delete at the top of the edit menu for easy access
                if st.button("❌ Delete Item", key=f"del_{i}", use_container_width=True):
                    st.session_state.cart.pop(i)
                    st.rerun()
                    
                if item["image"]:
                    st.image(item["image"], use_container_width=True, caption="Tap image to view full screen")
                
                st.write("**Edit Item:**")
                e_col1, e_col2 = st.columns(2)
                with e_col1:
                    edit_name = st.text_input("Name", item["name"], key=f"ename_{i}")
                    edit_price = st.number_input("Price", value=item["price"], min_value=0.0, step=0.50, key=f"eprice_{i}", placeholder="")
                with e_col2:
                    edit_qty = st.number_input("Quantity", value=item["qty"], min_value=1, step=1, key=f"eqty_{i}")
                
                st.write("**Update Image:**")
                edit_img_file = st.file_uploader("Upload new image", type=["jpg", "png", "jpeg"], key=f"efile_{i}")
                    
                # Save button dynamically updates the specific list item
                if st.button("💾 Save Changes", key=f"esave_{i}", type="primary", use_container_width=True):
                    st.session_state.cart[i]["name"] = edit_name
                    st.session_state.cart[i]["price"] = edit_price if edit_price is not None else 0.0
                    st.session_state.cart[i]["qty"] = edit_qty
                    
                    if edit_img_file:
                        st.session_state.cart[i]["image"] = edit_img_file
                        
                    st.rerun()

# --- The Grand Total (Bottom) ---
st.divider()
st.subheader(f"Grand Total: ₱{total_sum:.2f}")