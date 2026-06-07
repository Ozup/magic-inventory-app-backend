import requests

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal

from models.card import Card
from schemas.card import CardResponse, CardSearchResponse

import requests



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

    headers = {
        "User-Agent": "MagicInventoryApp/1.0"
    }

    response = requests.get(
        url,
        headers=headers
    )

    # Verificar si Scryfall encontró la carta
    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail="Card not found in Scryfall"
        )

    data = response.json()

    print("CARD:", data["name"])
    print("SET:", data.get("set"))
    print("PRICES:", data.get("prices"))

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

        set_name=data.get("set_name"),
        set_code=data.get("set"),
        collector_number=data.get("collector_number"),

        mana_cost=data.get("mana_cost"),
        oracle_text=data.get("oracle_text"),

        colors=",".join(
            data.get("colors", [])
        ),

        color_identity=",".join(
            data.get("color_identity", [])
        ),

        cmc=int(data.get("cmc", 0)),

        usd_price=float(
            data["prices"]["usd"]
        )
        if data.get("prices", {}).get("usd")
        else None,

        usd_foil_price=float(
            data["prices"]["usd_foil"]
        )
        if data.get("prices", {}).get("usd_foil")
        else None,

        image_url=data.get(
            "image_uris",
            {}
        ).get("normal")
    )

    db.add(new_card)

    db.commit()

    db.refresh(new_card)

    return new_card

@router.post("/resync-all")
def resync_all_cards(
    db: Session = Depends(get_db)
):

    # Obtener todas las cartas
    cards = db.query(Card).all()

    updated = 0

    for card in cards:
        # Buscar carta en Scryfall
        url = (
            "https://api.scryfall.com/cards/"
            f"{card.scryfall_id}"
        )
        print("URL:", url)
        headers = {
            "User-Agent":
            "MagicInventoryApp/1.0"
        }

        response = requests.get(
            url,
            headers=headers
        )
        # Si falla, continuar
        if response.status_code != 200:

            print(
                "ERROR",
                response.status_code
            )

            print(
                response.text
            )

            continue
        data = response.json()

        # Actualizar campos
        card.colors = ",".join(
            data.get("colors", [])
        )

        card.color_identity = ",".join(
            data.get("color_identity", [])
        )

        card.cmc = int(
            data.get("cmc", 0)
        )

        card.usd_price = (
            float(
                data["prices"]["usd"]
            )
            if data.get("prices", {}).get("usd")
            else None
        )

        card.usd_foil_price = (
            float(
                data["prices"]["usd_foil"]
            )
            if data.get("prices", {}).get("usd_foil")
            else None
        )
     

        updated += 1

    # Guardar cambios
    db.commit()

    return {
        "updated_cards": updated
    }

@router.get(
    "/search/{query}",
    response_model=list[CardSearchResponse]
)
def search_cards(query: str):

    url = f"https://api.scryfall.com/cards/search?q={query}"

    headers = {
        "User-Agent": "MagicInventoryApp/1.0"
    }

    response = requests.get(
        url,
        headers=headers
    )

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

@router.get("/autocomplete")
def autocomplete_cards(
    query: str
):

    SCRYFALL_HEADERS = {
    "User-Agent": "MagicInventoryApp/1.0"
    }
    response = requests.get(
    "https://api.scryfall.com/cards/search",
    headers=SCRYFALL_HEADERS,
    params={
        "q": query,
        "unique": "prints"
    }
    )

    data = response.json()

    cards = data.get("data", [])[:15]

    return [

        {
            "name": card["name"],

            "set_name": card["set_name"],

            "set_code": card.get(
                "set",
                ""
            ).upper(),

            "collector_number": card.get(
                "collector_number",
                ""
            ),

            "rarity": card.get(
                "rarity",
                ""
            ),

            "image_url":

                card.get(
                    "image_uris",
                    {}
                ).get(
                    "small"
                )

                or

                card.get(
                    "card_faces",
                    [{}]
                )[0].get(
                    "image_uris",
                    {}
                ).get(
                    "small",
                    ""
                ),

            "scryfall_id": card["id"]
        }

        for card in cards
    ]