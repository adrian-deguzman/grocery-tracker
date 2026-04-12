from pydantic import BaseModel
from typing import Optional

class Item(BaseModel):
    name: str
    price: float
    qty: int
    image: Optional[str] = None
    selected: bool = True

class ItemWithID(Item):
    id: str