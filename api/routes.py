from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import Item, ItemWithID
from core import database

router = APIRouter(prefix="/api/cart", tags=["cart"])

@router.get("", response_model=List[ItemWithID])
def get_cart():
    """Returns the whole grocery list."""
    return database.get_all_items()

@router.post("")
def add_item(item: Item):
    """Adds a new item to the list."""
    item_id = database.add_item(item)
    return {"message": "Item added", "id": item_id}

@router.put("/{item_id}")
def update_item(item_id: str, item: Item):
    """Updates an existing item (like toggling the checkbox)."""
    success = database.update_item(item_id, item)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item updated"}

@router.delete("/{item_id}")
def delete_item(item_id: str):
    """Deletes an item."""
    database.delete_item(item_id)
    return {"message": "Item deleted"}