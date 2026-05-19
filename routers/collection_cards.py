from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models.collection import Collection
from models.card import Card
from models.collection_card import CollectionCard

from schemas.collection_card import CollectionCardCreate


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
        quantity=data.quantity
    )

    db.add(new_collection_card)

    db.commit()

    db.refresh(new_collection_card)

    return new_collection_card