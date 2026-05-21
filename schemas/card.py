from pydantic import BaseModel


class CardResponse(BaseModel):
    id: int
    name: str
    scryfall_id: str

    image_url: str | None = None

    mana_cost: str | None = None

    rarity: str | None = None

    set_name: str | None = None

    set_code: str | None = None

    collector_number: str | None = None

    colors: str | None = None

    color_identity: str | None = None

    cmc: int | None = None

    class Config:
        from_attributes = True

class CardSearchResponse(BaseModel):
    name: str
    image_url: str | None = None