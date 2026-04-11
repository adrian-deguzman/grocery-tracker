import streamlit as st

# --- Page Config (Makes it look nice on mobile) ---
st.set_page_config(page_title="Grocery Tracker", page_icon="🛒", layout="centered")
st.title("🛒 My Grocery Tracker")

# --- Initialize Memory ---
# Because Streamlit reruns on every click, we must save our list in 'session_state'
if "cart" not in st.session_state:
    st.session_state.cart = []

# --- Pre-Calculate Math ---
# We calculate this first so we have the option to display it at the top of the app
total_sum = sum(item["price"] * item["qty"] for item in st.session_state.cart if item["selected"])

# --- Requirement 4 Update: Pin Total at Top (Sticky CSS) ---
pin_total = st.toggle("📌 Pin Total at Top", value=False)
if pin_total:
    # We use unsafe_allow_html=True to inject a fixed CSS banner
    st.markdown(
        f"""
        <style>
            .pinned-total {{
                position: fixed;
                top: 45px; /* Sits safely below the Streamlit menu bar */
                left: 0;
                right: 0;
                background-color: #2e7d32; /* High-visibility green */
                color: white;
                padding: 12px;
                text-align: center;
                font-size: 22px;
                font-weight: bold;
                z-index: 99999; /* Ensures it stays above all other elements */
                box-shadow: 0px 4px 6px rgba(0,0,0,0.3);
            }}
            /* Add some padding to the main container so the banner doesn't hide the top items */
            .block-container {{
                padding-top: 80px;
            }}
        </style>
        <div class="pinned-total">
            Grand Total: ₱{total_sum:.2f}
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Add New Item Section ---
with st.expander("➕ Add New Item", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        item_name = st.text_input("Item Name")
        # Setting value=None removes the default 0.00 so the field is completely empty
        item_price = st.number_input("Price per piece", min_value=0.0, step=0.50, value=None, placeholder="0.00")
    
    with col2:
        item_qty = st.number_input("Quantity", min_value=1, step=1)
        item_image = st.file_uploader("Upload or Take Picture", type=["jpg", "png", "jpeg"])

    if st.button("Add to Cart", type="primary"):
        if item_name:
            # Create a dictionary for the new item
            new_item = {
                "name": item_name,
                "price": item_price if item_price is not None else 0.0, # Defaults to 0.0 if left completely blank
                "qty": item_qty,
                "image": item_image,
                "selected": True 
            }
            # Add it to our saved memory
            st.session_state.cart.append(new_item)
            st.success(f"Added {item_name}!")
            st.rerun() # Refresh the page to show the new list
        else:
            st.error("Please give the item a name!")

# --- List Items, Toggles, and Editing ---
st.header("🧾 Your List")

if not st.session_state.cart:
    st.info("Your cart is empty. Add something above!")
else:
    # Loop through our saved items
    for i, item in enumerate(st.session_state.cart):
        # Create a nice row layout: [Checkbox] [Text] [Delete Button]
        col_check, col_details, col_del = st.columns([1, 6, 1], vertical_alignment="center")
        
        with col_check:
            # Requirement 1: Fixed empty label warning. 
            # We provide a label string but use label_visibility="collapsed" to hide it.
            is_checked = st.checkbox(
                f"Select {item['name']}", 
                value=item["selected"], 
                key=f"check_{i}",
                label_visibility="collapsed" 
            )
            # Instantly update state if clicked
            if is_checked != item["selected"]:
                st.session_state.cart[i]["selected"] = is_checked
                st.rerun()
        
        with col_details:
            st.markdown(f"**{item['name']}** &nbsp;|&nbsp; {item['qty']} x ₱{item['price']:.2f}")
        
        with col_del:
            if st.button("❌", key=f"del_{i}"):
                st.session_state.cart.pop(i) # Remove item
                st.rerun()

        # Requirement 2: Editable list and Full Screen Image Viewer
        with st.expander("✏️ Edit Details / 📷 View Image"):
            if item["image"]:
                # use_container_width makes it fit nicely. 
                # Note: You can tap/click this image natively in Streamlit to view it Full Screen!
                st.image(item["image"], use_container_width=True, caption="Tap image to view full screen")
            
            st.write("**Edit Item:**")
            e_col1, e_col2 = st.columns(2)
            with e_col1:
                edit_name = st.text_input("Name", item["name"], key=f"ename_{i}")
                edit_price = st.number_input("Price", value=item["price"], min_value=0.0, step=0.50, key=f"eprice_{i}")
            with e_col2:
                edit_qty = st.number_input("Quantity", value=item["qty"], min_value=1, step=1, key=f"eqty_{i}")
            
            st.write("**Update Image:**")
            edit_img_file = st.file_uploader("Upload new image", type=["jpg", "png", "jpeg"], key=f"efile_{i}")
                
            if st.button("💾 Save Changes", key=f"esave_{i}"):
                # Update text values
                st.session_state.cart[i]["name"] = edit_name
                st.session_state.cart[i]["price"] = edit_price
                st.session_state.cart[i]["qty"] = edit_qty
                
                # Update image ONLY if a new one was uploaded
                if edit_img_file:
                    st.session_state.cart[i]["image"] = edit_img_file
                    
                st.rerun()

# --- The Grand Total (Bottom) ---
st.divider()
st.subheader(f"Grand Total: ₱{total_sum:.2f}")