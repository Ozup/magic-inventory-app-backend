import requests

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal

from models.card import Card
from schemas.card import CardResponse, CardSearchResponse



router = APIRouter(
    prefix="/cards",
    tags=["Cards"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/sync/{card_name}")
def sync_card(
    card_name: str,
    db: Session = Depends(get_db)
):

    # Buscar carta en Scryfall
    url = f"https://api.scryfall.com/cards/named?fuzzy={card_name}"

    response = requests.get(url)

    # Verificar si Scryfall encontró la carta
    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail="Card not found in Scryfall"
        )

    data = response.json()

    # Buscar si ya existe en PostgreSQL
    existing_card = db.query(Card).filter(
        Card.scryfall_id == data["id"]
    ).first()

    # Si ya existe, devolverla
    if existing_card:
        return existing_card

    # Crear nueva carta
    new_card = Card(
        scryfall_id=data["id"],
        name=data["name"],
        type_line=data.get("type_line"),
        rarity=data.get("rarity"),
        mana_cost=data.get("mana_cost"),
        oracle_text=data.get("oracle_text"),
        image_url=data.get("image_uris", {}).get("normal")
    )

    db.add(new_card)

    db.commit()

    db.refresh(new_card)

    return new_card

@router.get(
    "/search/{query}",
    response_model=list[CardSearchResponse]
)
def search_cards(query: str):

    url = f"https://api.scryfall.com/cards/search?q={query}"

    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail="No cards found"
        )

    data = response.json()

    results = []

    for card in data["data"][:10]:

        results.append({
            "name": card["name"],
            "image_url": card.get(
                "image_uris",
                {}
            ).get("normal")
        })

    return results