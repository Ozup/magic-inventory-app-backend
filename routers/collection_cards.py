from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models.collection import Collection
from models.card import Card
from models.collection_card import CollectionCard

from schemas.collection_card import CollectionCardCreate

from schemas.collection_card import CollectionCardCreate, CollectionCardResponse

import requests


router = APIRouter(
    prefix="/collections",
    tags=["Collection Cards"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/{collection_id}/cards")
def add_card_to_collection(
    collection_id: int,
    data: CollectionCardCreate,
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

    # Buscar carta
    card = db.query(Card).filter(
        Card.id == data.card_id
    ).first()

    if not card:
        raise HTTPException(
            status_code=404,
            detail="Card not found"
        )

    # Verificar si ya existe en la colección
    existing = db.query(CollectionCard).filter(
        CollectionCard.collection_id == collection_id,
        CollectionCard.card_id == data.card_id
    ).first()

    # Si ya existe, aumentar quantity
    if existing:
        existing.quantity += data.quantity

        db.commit()
        db.refresh(existing)

        return existing

    # Si no existe, crear nueva relación
    new_collection_card = CollectionCard(
        collection_id=collection_id,
        card_id=data.card_id,
        quantity=data.quantity,
        is_commander=data.is_commander
    )

    db.add(new_collection_card)

    db.commit()

    db.refresh(new_collection_card)

    return new_collection_card

@router.get(
    "/{collection_id}/cards",
    response_model=list[CollectionCardResponse]
)
def get_collection_cards(
    collection_id: int,
    color: str | None = None,
    type: str | None = None,
    rarity: str | None = None,
    name: str | None = None,

    limit: int = 20,
    offset: int = 0,

    sort_by: str | None = None,

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

    # Query base
    query = db.query(CollectionCard).join(Card).filter(
        CollectionCard.collection_id == collection_id
    )

    # Filtrar por color
    if color:

        query = query.filter(
            Card.color_identity.contains(color)
        )

    # Filtrar por tipo
    if type:

        query = query.filter(
            Card.type_line.contains(type)
        )

    # Filtrar por rareza
    if rarity:

        query = query.filter(
            Card.rarity.ilike(f"%{rarity}%")
        )

    # Filtrar por nombre
    if name:

        query = query.filter(
            Card.name.ilike(f"%{name}%")
        )

    # Sorting
    if sort_by == "name":

        query = query.order_by(Card.name)

    elif sort_by == "cmc":

        query = query.order_by(Card.cmc)

    elif sort_by == "rarity":

        query = query.order_by(Card.rarity)

    # Pagination
    cards = query.offset(offset).limit(limit).all()

    return cards

@router.delete("/{collection_id}/cards/{card_id}")
def remove_card_from_collection(
    collection_id: int,
    card_id: int,
    db: Session = Depends(get_db)
):

    # Buscar relación CollectionCard
    collection_card = db.query(CollectionCard).filter(
        CollectionCard.collection_id == collection_id,
        CollectionCard.card_id == card_id
    ).first()

    # Verificar si existe
    if not collection_card:
        raise HTTPException(
            status_code=404,
            detail="Card not found in collection"
        )

    # Eliminar relación
    db.delete(collection_card)

    db.commit()

    return {
        "message": "Card removed from collection"
    }

@router.post("/{collection_id}/cards/by-name/{card_name}")
def add_card_to_collection_by_name(
    collection_id: int,
    card_name: str,
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

    # Buscar carta en Scryfall
    url = f"https://api.scryfall.com/cards/named?fuzzy={card_name}"

    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail="Card not found in Scryfall"
        )

    data = response.json()

    # Buscar carta localmente
    card = db.query(Card).filter(
        Card.scryfall_id == data["id"]
    ).first()

    # Si no existe, crear carta
    if not card:

        card = Card(
            scryfall_id=data["id"],
            name=data["name"],

            type_line=data.get("type_line"),

            rarity=data.get("rarity"),

            mana_cost=data.get("mana_cost"),

            oracle_text=data.get("oracle_text"),

            set_name=data.get("set_name"),

            set_code=data.get("set"),

            collector_number=data.get(
                "collector_number"
            ),

            colors=",".join(
                data.get("colors", [])
            ),

            color_identity=",".join(
                data.get("color_identity", [])
            ),

            cmc=int(data.get("cmc", 0)),

            image_url=data.get(
                "image_uris",
                {}
            ).get("normal")
        )

        db.add(card)

        db.commit()

        db.refresh(card)

    # Buscar relación existente
    existing = db.query(CollectionCard).filter(
        CollectionCard.collection_id == collection_id,
        CollectionCard.card_id == card.id
    ).first()

    # Si ya existe, aumentar quantity
    if existing:

        existing.quantity += 1

        db.commit()

        db.refresh(existing)

        return existing

    # Crear nueva relación
    new_collection_card = CollectionCard(
        collection_id=collection_id,
        card_id=card.id,
        quantity=1,
        is_commander=False
    )

    db.add(new_collection_card)

    db.commit()

    db.refresh(new_collection_card)

    return new_collection_card


