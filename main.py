from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI(title="Grocery Tracker API")

# --- Database Simulation ---
db_cart = {}

# --- Data Models (Pydantic) ---
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

# --- Serve Frontend ---
# This line tells FastAPI to serve any files inside the "static" folder to the browser.
# html=True means it will automatically look for an "index.html" file to display.
app.mount("/", StaticFiles(directory="static", html=True), name="static")