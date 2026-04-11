import streamlit as st

# --- Page Config (Makes it look nice on mobile) ---
st.set_page_config(page_title="Grocery Tracker", page_icon="🛒", layout="centered")
st.title("🛒 My Grocery Tracker")

# --- Initialize Memory ---
# Because Streamlit reruns on every click, we must save our list in 'session_state'
if "cart" not in st.session_state:
    st.session_state.cart = []

# --- Requirement 1, 2, & 3: Add Item, Image, Price, Quantity ---
with st.expander("➕ Add New Item", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        item_name = st.text_input("Item Name")
        item_price = st.number_input("Price per piece", min_value=0.0, step=0.50)
    
    with col2:
        item_qty = st.number_input("Quantity", min_value=1, step=1)
        # Using camera_input instead of file_uploader is great for mobile phones!
        # You can swap this to st.file_uploader("Upload Image") if testing on PC.
        item_image = st.file_uploader("Upload or Take Picture", type=["jpg", "png", "jpeg"])

    if st.button("Add to Cart", type="primary"):
        if item_name:
            # Create a dictionary for the new item
            new_item = {
                "name": item_name,
                "price": item_price,
                "qty": item_qty,
                "image": item_image,
                "selected": True # Requirement 4: ability to deselect (defaults to True)
            }
            # Add it to our saved memory
            st.session_state.cart.append(new_item)
            st.success(f"Added {item_name}!")
            st.rerun() # Refresh the page to show the new list
        else:
            st.error("Please give the item a name!")

# --- Requirement 4: List Items, Toggles, and Sum Total ---
st.header("🧾 Your List")

total_sum = 0.0

if not st.session_state.cart:
    st.info("Your cart is empty. Add something above!")
else:
    # Loop through our saved items
    for i, item in enumerate(st.session_state.cart):
        # Create a nice row layout: [Checkbox] [Text] [Image] [Delete Button]
        col_check, col_details, col_img, col_del = st.columns([1, 4, 2, 1], vertical_alignment="center")
        
        with col_check:
            # The checkbox state is tied to our dictionary
            is_checked = st.checkbox("", value=item["selected"], key=f"check_{i}")
            st.session_state.cart[i]["selected"] = is_checked
        
        with col_details:
            st.write(f"**{item['name']}**")
            st.write(f"{item['qty']} x ${item['price']:.2f}")
        
        with col_img:
            if item["image"]:
                st.image(item["image"], width=50) # Show a small thumbnail
        
        with col_del:
            if st.button("❌", key=f"del_{i}"):
                st.session_state.cart.pop(i) # Remove item
                st.rerun()

        # Add to total ONLY if the checkbox is ticked
        if is_checked:
            total_sum += (item["price"] * item["qty"])

# --- The Grand Total ---
st.divider()
st.subheader(f"Grand Total: ${total_sum:.2f}")