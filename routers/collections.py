from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal

from models.collection import Collection

from schemas.collection import (
    CollectionCreate,
    CollectionResponse
)


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