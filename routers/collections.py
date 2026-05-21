from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal

from models.collection import Collection, CollectionType

from schemas.collection import CollectionCreate, CollectionResponse

import requests

from models.collection_card import CollectionCard
from models.card import Card


router = APIRouter(
    prefix="/collections",
    tags=["Collections"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CollectionResponse)
def create_collection(
    data: CollectionCreate,
    db: Session = Depends(get_db)
):

    new_collection = Collection(
        name=data.name,
        description=data.description,
        type=data.type,
        set_code=data.set_code
    )

    db.add(new_collection)

    db.commit()

    db.refresh(new_collection)

    return new_collection

@router.get("/", response_model=list[CollectionResponse])
def get_collections(
    db: Session = Depends(get_db)
):

    collections = db.query(Collection).all()

    return collections

@router.get("/{collection_id}", response_model=CollectionResponse)
def get_collection(
    collection_id: int,
    db: Session = Depends(get_db)
):

    collection = db.query(Collection).filter(
        Collection.id == collection_id
    ).first()

    if not collection:
        raise HTTPException(
            status_code=404,
            detail="Collection not found"
        )

    return collection

@router.delete("/{collection_id}")
def delete_collection(
    collection_id: int,
    db: Session = Depends(get_db)
):

    collection = db.query(Collection).filter(
        Collection.id == collection_id
    ).first()

    if not collection:
        raise HTTPException(
            status_code=404,
            detail="Collection not found"
        )

    db.delete(collection)

    db.commit()

    return {
        "message": "Collection deleted"
    }

@router.get("/{collection_id}/progress")
def get_collection_progress(

    collection_id: int,
    db: Session = Depends(get_db)
):

    # Buscar colección
    collection = db.query(Collection).filter(
        Collection.id == collection_id
    ).first()

    if not collection:
        raise HTTPException(
            status_code=404,
            detail="Collection not found"
        )

    # Verificar que sea álbum
    if collection.type != CollectionType.ALBUM:
        raise HTTPException(
            status_code=400,
            detail="Progress tracking only available for albums"
        )

    # Contar cartas adquiridas del set
    owned_cards = db.query(CollectionCard).join(Card).filter(
        CollectionCard.collection_id == collection_id,
        Card.set_code == collection.set_code
    ).count()

    # Consultar total de cartas del set en Scryfall
    url = f"https://api.scryfall.com/cards/search?q=e:{collection.set_code}"

    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail="Could not fetch set data"
        )

    data = response.json()

    total_cards = data.get("total_cards", 0)

    # Calcular porcentaje
    completion_percentage = 0

    if total_cards > 0:
        completion_percentage = round(
            (owned_cards / total_cards) * 100,
            2
        )

    return {
        "set_name": collection.name,
        "set_code": collection.set_code,
        "owned_cards": owned_cards,
        "total_cards": total_cards,
        "completion_percentage": completion_percentage
    }

@router.get("/{collection_id}/deck-stats")
def get_deck_stats(
    collection_id: int,
    db: Session = Depends(get_db)
):

    # Buscar colección
    collection = db.query(Collection).filter(
        Collection.id == collection_id
    ).first()

    if not collection:
        raise HTTPException(
            status_code=404,
            detail="Collection not found"
        )

    # Verificar que sea deck
    if collection.type != CollectionType.DECK:
        raise HTTPException(
            status_code=400,
            detail="Deck stats only available for decks"
        )

    # Obtener cartas del deck
    cards = db.query(CollectionCard).join(Card).filter(
        CollectionCard.collection_id == collection_id
    ).all()

    # Total de cartas
    total_cards = 0

    for item in cards:
        total_cards += item.quantity

    # Cartas únicas
    unique_cards = len(cards)

    # Distribución de tipos
    types = {}

    # Curva de mana
    mana_curve = {}

    for item in cards:

        type_line = item.card.type_line

        if type_line:

            main_type = type_line.split("—")[0].strip()

            if main_type not in types:
                types[main_type] = 0

            types[main_type] += item.quantity

        # Mana curve
        mana_cost = item.card.mana_cost

        if mana_cost:

            mana_value = mana_cost.count("{")

            mana_value = str(mana_value)

            if mana_value not in mana_curve:
                mana_curve[mana_value] = 0

            mana_curve[mana_value] += item.quantity

    return {
        "total_cards": total_cards,
        "unique_cards": unique_cards,
        "types": types,
        "mana_curve": mana_curve
    }