import uuid
from models.schemas import Item, StatusEnum

# Simulated in-memory database
db_cart = {}

def get_all_items():
    return [{"id": k, **v.model_dump()} for k, v in db_cart.items()]

def add_item(item: Item):
    # Check if an item with the same name, price, and status already exists
    for existing_id, existing_item in db_cart.items():
        if (existing_item.name.strip().lower() == item.name.strip().lower() and 
            existing_item.price == item.price and 
            existing_item.status == item.status):
            
            # Merge by adding the quantities together
            existing_item.qty += item.qty
            
            # If the new submission has an image but the old one didn't, save the new image
            if item.image and not existing_item.image:
                existing_item.image = item.image
                
            return existing_id

    # If no match is found, add it as a brand-new item
    item_id = str(uuid.uuid4())
    db_cart[item_id] = item
    return item_id

def update_item(item_id: str, item: Item):
    if item_id in db_cart:
        db_cart[item_id] = item
        return True
    return False

def update_item_status(item_id: str, status: StatusEnum):
    if item_id in db_cart:
        db_cart[item_id].status = status
        return True
    return False

def delete_item(item_id: str):
    if item_id in db_cart:
        del db_cart[item_id]
        return True
    return False