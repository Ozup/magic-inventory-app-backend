from pydantic import BaseModel
from schemas.card import CardResponse

class CollectionCardCreate(BaseModel):
    card_id: int
    quantity: int = 1
    is_commander: bool = False

class CollectionCardResponse(BaseModel):
    id: int
    quantity: int
    card: CardResponse
    is_commander: bool = False

    class Config:
        from_attributes = True
