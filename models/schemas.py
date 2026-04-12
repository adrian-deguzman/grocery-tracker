from pydantic import BaseModel
from typing import Optional
from enum import Enum

class StatusEnum(str, Enum):
    planned = "planned"
    in_cart = "in_cart"

class Item(BaseModel):
    name: str
    price: Optional[float] = 0.0  # Allows null or 0, defaults to 0.0
    qty: int
    image: Optional[str] = None   # Allows null
    selected: bool = True
    status: StatusEnum = StatusEnum.in_cart  # Defaults to in_cart for backwards compatibility

class ItemWithID(Item):
    id: str

# Schema specifically for the PATCH endpoint
class ItemStatusUpdate(BaseModel):
    status: StatusEnum