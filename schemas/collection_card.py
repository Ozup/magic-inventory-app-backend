from pydantic import BaseModel

class CollectionCardCreate(BaseModel):
    card_id: int
    quantity: int = 1

class CollectionCardResponse(BaseModel):
    id: int
    collection_id: int
    card_id: int
    quantity: int

    class Config:
        from_attributes = True
