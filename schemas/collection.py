from pydantic import BaseModel
from models.enums import CollectionType


class CollectionCreate(BaseModel):
    name: str
    type: CollectionType
    description: str | None = None
    set_code: str | None = None
    deck_format: str | None = None


class CollectionResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    type: CollectionType
    set_code: str | None = None
    deck_format: str | None = None

    class Config:
        from_attributes = True

class CollectionUpdate(BaseModel):
    name: str | None = None
    type: CollectionType | None = None