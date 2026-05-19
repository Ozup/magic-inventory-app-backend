from pydantic import BaseModel

class CollectionCardCreate(BaseModel):
    card_id: int
    quantity: int = 1