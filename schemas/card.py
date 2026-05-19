from pydantic import BaseModel


class CardResponse(BaseModel):
    id: int
    name: str
    scryfall_id: str
    image_url: str | None = None
    mana_cost: str | None = None
    rarity: str | None = None

    class Config:
        from_attributes = True

class CardSearchResponse(BaseModel):
    name: str
    image_url: str | None = None