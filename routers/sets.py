import requests

from fastapi import APIRouter, HTTPException


router = APIRouter(
    prefix="/sets",
    tags=["Sets"]
)


@router.get("/search/{query}")
def search_sets(
    query: str,
    include_special: bool = False
):

    url = "https://api.scryfall.com/sets"

    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail="Could not fetch sets"
        )

    data = response.json()

    allowed_types = ["expansion", "core", "masters"]

    if include_special:
        allowed_types.extend([
            "commander",
            "token",
            "promo",
            "alchemy",
            "memorabilia"
        ])

    results = []

    for set_data in data["data"]:

        set_name = set_data.get("name", "").lower()

        set_type = set_data.get("set_type")

        if (
            query.lower() in set_name
            and set_type in allowed_types
        ):

            results.append({
                "code": set_data.get("code"),
                "name": set_data.get("name")
            })

    return results[:10]