import uuid
from models.schemas import Item, StatusEnum

# Simulated in-memory database
db_cart = {}

def get_all_items():
    return [{"id": k, **v.model_dump()} for k, v in db_cart.items()]

def add_item(item: Item):
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