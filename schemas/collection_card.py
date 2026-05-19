from pydantic import BaseModel
from schemas.card import CardResponse

class CollectionCardCreate(BaseModel):
    card_id: int
    quantity: int = 1

class CollectionCardResponse(BaseModel):
    id: int
    quantity: int
    card: CardResponse

    class Config:
        from_attributes = True
