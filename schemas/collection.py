from pydantic import BaseModel
from models.enums import CollectionType


class CollectionCreate(BaseModel):
    name: str
    type: CollectionType
    set_code: str | None = None


class CollectionResponse(BaseModel):
    id: int
    name: str
    type: CollectionType

    class Config:
        from_attributes = True

class CollectionUpdate(BaseModel):
    name: str | None = None
    type: CollectionType | None = None