from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal

from models.collection import Collection, CollectionType

from schemas.collection import CollectionCreate, CollectionResponse

import requests

from models.collection_card import CollectionCard
from models.card import Card

from models.enums import CollectionType, DeckFormat



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
        set_code=data.set_code,
        deck_format=data.deck_format
    )

    db.add(new_collection)

    db.commit()

    db.refresh(new_collection)

    # =========================
    # AUTO IMPORT ALBUM CARDS
    # =========================

    if (
        new_collection.type ==
        CollectionType.ALBUM
        and
        new_collection.set_code
    ):

        url = (
            "https://api.scryfall.com/"
            f"cards/search?q=set:{new_collection.set_code}"
            "&unique=prints"
)
        while url:

            response = requests.get(url)

            if response.status_code != 200:
                break

            data = response.json()

            cards_data = data.get(
                "data",
                []
            )

            for card_data in cards_data:

                # Buscar carta existente
                existing_card = db.query(Card).filter(
                    Card.scryfall_id ==
                    card_data["id"]
                ).first()

                # Obtener imagen
                image_url = (

                    card_data.get(
                        "image_uris",
                        {}
                    ).get(
                        "normal"
                    )

                    or

                    card_data.get(
                        "card_faces",
                        [{}]
                    )[0].get(
                        "image_uris",
                        {}
                    ).get(
                        "normal",
                        ""
                    )
                )

                # Crear carta si no existe
                if not existing_card:

                    existing_card = Card(

                        scryfall_id=
                            card_data["id"],

                        name=
                            card_data["name"],

                        type_line=
                            card_data.get(
                                "type_line"
                            ),

                        rarity=
                            card_data.get(
                                "rarity"
                            ),

                        mana_cost=
                            card_data.get(
                                "mana_cost"
                            ),

                        oracle_text=
                            card_data.get(
                                "oracle_text"
                            ),

                        set_name=
                            card_data.get(
                                "set_name"
                            ),

                        set_code=
                            card_data.get(
                                "set"
                            ),

                        collector_number=
                            card_data.get(
                                "collector_number"
                            ),

                        colors=",".join(
                            card_data.get(
                                "colors",
                                []
                            )
                        ),

                        color_identity=",".join(
                            card_data.get(
                                "color_identity",
                                []
                            )
                        ),

                        cmc=int(
                            card_data.get(
                                "cmc",
                                0
                            )
                        ),

                        image_url=image_url
                    )

                    db.add(existing_card)

                    db.commit()

                    db.refresh(existing_card)

                # Verificar relación existente
                existing_relation = (
                    db.query(CollectionCard)
                    .filter(
                        CollectionCard.collection_id
                        == new_collection.id,

                        CollectionCard.card_id
                        == existing_card.id
                    )
                    .first()
                )

                # Crear relación
                if not existing_relation:

                    relation = CollectionCard(

                        collection_id=
                            new_collection.id,

                        card_id=
                            existing_card.id,

                        quantity=0,

                        is_commander=False
                    )

                    db.add(relation)

            db.commit()

            # =========================
            # NEXT PAGE
            # =========================

            if data.get("has_more"):

                url = data.get(
                    "next_page"
                )

            else:

                url = None

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

    # =========================
    # DELETE RELATIONS
    # =========================

    db.query(CollectionCard).filter(
        CollectionCard.collection_id
        == collection_id
    ).delete()

    # =========================
    # DELETE COLLECTION
    # =========================

    db.delete(collection)

    db.commit()

    return {
        "message":
        "Collection deleted"
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

    # Distribución de colores
    color_distribution = {}

    # Mana value total
    total_mana_value = 0

    for item in cards:

        # =====================
        # TYPES
        # =====================

        type_line = item.card.type_line

        if type_line:

            main_type = type_line.split(
                "—"
            )[0].strip()

            if main_type not in types:
                types[main_type] = 0

            types[main_type] += item.quantity

        # =====================
        # MANA CURVE
        # =====================

        if item.card.cmc is not None:

            mana_value = str(item.card.cmc)

            if mana_value not in mana_curve:
                mana_curve[mana_value] = 0

            mana_curve[mana_value] += (
                item.quantity
            )

            total_mana_value += (
                item.card.cmc * item.quantity
            )

        # =====================
        # COLORS
        # =====================

        if item.card.colors:

            colors = item.card.colors.split(",")

            for color in colors:

                if color not in color_distribution:
                    color_distribution[color] = 0

                color_distribution[color] += (
                    item.quantity
                )

    # Average mana value
    average_mana_value = 0

    if total_cards > 0:

        average_mana_value = round(
            total_mana_value / total_cards,
            2
        )

    return {
        "total_cards": total_cards,

        "unique_cards": unique_cards,

        "average_mana_value":
            average_mana_value,

        "types": types,

        "mana_curve": mana_curve,

        "color_distribution":
            color_distribution
    }

@router.get("/{collection_id}/deck-validation")
def validate_deck(
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
            detail="Validation only available for decks"
        )

    # Verificar formato
    if not collection.deck_format:
        raise HTTPException(
            status_code=400,
            detail="Deck format not defined"
        )

    # Obtener cartas
    cards = db.query(CollectionCard).join(Card).filter(
        CollectionCard.collection_id == collection_id
    ).all()

    # Lista de errores
    errors = []

    # =========================
    # COMMANDER VALIDATION
    # =========================

    if collection.deck_format == DeckFormat.COMMANDER:

        # Total de cartas
        total_cards = 0

        for item in cards:
            total_cards += item.quantity

        # Debe tener exactamente 100 cartas
        if total_cards != 100:

            errors.append(
                "Commander decks must contain exactly 100 cards"
            )

        # Singleton rule
        for item in cards:

            if item.quantity > 1:

                errors.append(
                    f"{item.card.name} exceeds singleton limit"
                )

        # =========================
        # COMMANDER COLOR IDENTITY
        # =========================

        commander = None

        # Buscar commander
        for item in cards:

            if item.is_commander:
                commander = item
                break

        # Validar que exista commander
        if not commander:

            errors.append(
                "Commander deck must have a commander"
            )

        else:

            # Colores permitidos
            commander_colors = set(
                commander.card.color_identity.split(",")
            )

            # Revisar todas las cartas
            for item in cards:

                if item.card.color_identity:

                    card_colors = set(
                        item.card.color_identity.split(",")
                    )

                    # Validar colores
                    if not card_colors.issubset(
                        commander_colors
                    ):

                        errors.append(
                            f"{item.card.name} "
                            "is outside commander's "
                            "color identity"
                        )

    # Resultado final
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
