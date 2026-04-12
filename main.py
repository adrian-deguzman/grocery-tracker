from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI(title="Grocery Tracker API")

# --- Database Simulation ---
# We use a simple Python dictionary in memory for now. 
# (You can easily swap this to Firestore later!)
db_cart = {}

# --- Data Models (Pydantic) ---
# This ensures data coming from the frontend is perfectly formatted
class Item(BaseModel):
    name: str
    price: float
    qty: int
    image: Optional[str] = None
    selected: bool = True

class ItemWithID(Item):
    id: str

# --- API Routes (The Backend Engine) ---
@app.get("/api/cart", response_model=List[ItemWithID])
def get_cart():
    """Returns the whole grocery list."""
    return [{"id": k, **v.model_dump()} for k, v in db_cart.items()]

@app.post("/api/cart")
def add_item(item: Item):
    """Adds a new item to the list."""
    item_id = str(uuid.uuid4())
    db_cart[item_id] = item
    return {"message": "Item added", "id": item_id}

@app.put("/api/cart/{item_id}")
def update_item(item_id: str, item: Item):
    """Updates an existing item (like toggling the checkbox)."""
    if item_id not in db_cart:
        raise HTTPException(status_code=404, detail="Item not found")
    db_cart[item_id] = item
    return {"message": "Item updated"}

@app.delete("/api/cart/{item_id}")
def delete_item(item_id: str):
    """Deletes an item."""
    if item_id in db_cart:
        del db_cart[item_id]
    return {"message": "Item deleted"}


# --- The Frontend UI (HTML/CSS/JavaScript) ---
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grocery Tracker</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 pb-20">

    <div class="sticky top-0 bg-green-600 text-white p-4 shadow-md z-50">
        <h1 class="text-2xl font-bold text-center">Grand Total: ₱<span id="grand-total">0.00</span></h1>
    </div>

    <div class="max-w-md mx-auto p-4 mt-4">
        
        <div class="bg-white p-4 rounded-lg shadow mb-6">
            <h2 class="font-bold mb-2">➕ Add New Item</h2>
            <input type="text" id="itemName" placeholder="Item Name" class="w-full border p-2 rounded mb-2">
            <div class="flex gap-2 mb-2">
                <input type="number" id="itemPrice" placeholder="Price (₱)" class="w-1/2 border p-2 rounded" step="0.5">
                <input type="number" id="itemQty" placeholder="Qty" value="1" class="w-1/2 border p-2 rounded">
            </div>
            <input type="file" id="itemImage" accept="image/*" class="w-full text-sm mb-2">
            <button onclick="addItem()" class="w-full bg-blue-600 text-white font-bold py-2 rounded">Add to Cart</button>
        </div>

        <h2 class="text-xl font-bold mb-2">🧾 Your List</h2>
        <div id="cart-list" class="flex flex-col gap-2">
            </div>

    </div>

    <script>
        // --- JavaScript Logic (Talking to FastAPI) ---
        
        // Load items when page opens
        window.onload = fetchItems;

        async function fetchItems() {
            const response = await fetch('/api/cart');
            const items = await response.json();
            renderList(items);
        }

        async function addItem() {
            const name = document.getElementById('itemName').value;
            const price = parseFloat(document.getElementById('itemPrice').value) || 0;
            const qty = parseInt(document.getElementById('itemQty').value) || 1;
            const imageFile = document.getElementById('itemImage').files[0];

            if (!name) return alert("Need a name!");

            // Convert image to Base64 text if it exists
            let imageB64 = null;
            if (imageFile) {
                imageB64 = await toBase64(imageFile);
            }

            const payload = { name, price, qty, image: imageB64, selected: true };

            await fetch('/api/cart', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            // Clear inputs and reload list
            document.getElementById('itemName').value = '';
            document.getElementById('itemPrice').value = '';
            document.getElementById('itemImage').value = '';
            fetchItems();
        }

        async function toggleItem(id, itemData) {
            itemData.selected = !itemData.selected;
            await fetch(`/api/cart/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(itemData)
            });
            fetchItems();
        }

        async function deleteItem(id) {
            await fetch(`/api/cart/${id}`, { method: 'DELETE' });
            fetchItems();
        }

        // --- UI Rendering ---
        function renderList(items) {
            const listDiv = document.getElementById('cart-list');
            listDiv.innerHTML = ''; // clear current list
            let total = 0;

            if (items.length === 0) {
                listDiv.innerHTML = '<p class="text-gray-500 italic">Cart is empty.</p>';
            }

            items.forEach(item => {
                if (item.selected) {
                    total += (item.price * item.qty);
                }

                // Create the exact UI layout you wanted: Checkbox | Details | Delete
                const itemHTML = `
                    <div class="bg-white p-3 rounded-lg shadow flex items-center gap-3">
                        <input type="checkbox" class="w-6 h-6" ${item.selected ? 'checked' : ''} 
                               onchange='toggleItem("${item.id}", ${JSON.stringify(item)})'>
                        
                        <div class="flex-grow">
                            <p class="font-bold text-lg leading-tight">${item.name}</p>
                            <p class="text-gray-600 text-sm">${item.qty} x ₱${item.price.toFixed(2)}</p>
                        </div>
                        
                        ${item.image ? `<img src="${item.image}" class="w-12 h-12 object-cover rounded">` : ''}
                        
                        <button onclick='deleteItem("${item.id}")' class="text-red-500 text-xl font-bold px-2">❌</button>
                    </div>
                `;
                listDiv.innerHTML += itemHTML;
            });

            document.getElementById('grand-total').innerText = total.toFixed(2);
        }

        // Helper function for images
        const toBase64 = file => new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
    </script>
</body>
</html>
"""

# Serve the HTML when someone goes to the main URL
@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return HTML_UI