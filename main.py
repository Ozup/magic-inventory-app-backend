import requests
from models.collection import Collection
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from pydantic import BaseModel #FastAPI lee, valida y convierte con esto, sirve para el CRUD


from schemas.collection import CollectionCreate, CollectionResponse, CollectionUpdate

from routers import collection_cards, cards, collections, sets


app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/search/{card_name}")
def search_card(card_name: str):

    url = f"https://api.scryfall.com/cards/named?fuzzy={card_name}"

    response = requests.get(url)

    data = response.json()

    return {
        "name": data["name"],
        "image": data["image_uris"]["normal"]
    }

@app.get("/collections")
def get_collections(db: Session = Depends(get_db)):
    collections = db.query(Collection).all()
    return [
    {
        "id": collection.id,
        "name": collection.name
    }
    for collection in collections
]

@app.get("/collections/{collection_id}")
def get_collection(collection_id: int, db: Session = Depends(get_db)):

    collection = db.query(Collection).filter(
        Collection.id == collection_id
    ).first()

    return collection

@app.post("/collections", response_model=CollectionResponse) # Le explico a FastAPI como quiero mi respuesta
def create_collection(
    collection: CollectionCreate,
    db: Session = Depends(get_db)
):

    new_collection = Collection(
        name=collection.name, type=collection.type
    )

    db.add(new_collection)

    db.commit()

    db.refresh(new_collection)

    return new_collection

@app.delete("/collections/{collection_id}")
def delete_collection(
    collection_id: int,
    db: Session = Depends(get_db)
):

    collection = db.query(Collection).filter(
        Collection.id == collection_id
    ).first()

    if not collection:
        return {"error": "Collection not found"}

    db.delete(collection)

    db.commit()

    return {"message": "Collection deleted successfully"}

@app.put("/collections/{collection_id}")
def update_collection(
    collection_id: int,
    collection_data: CollectionUpdate,
    db: Session = Depends(get_db)
):

    collection = db.query(Collection).filter(
        Collection.id == collection_id
    ).first()

    if not collection:
        return {"error": "Collection not found"}

    update_data = collection_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(collection, key, value)

    db.commit()

    db.refresh(collection)

    return collection

app.include_router(collection_cards.router)

app.include_router(cards.router)

app.include_router(sets.router)