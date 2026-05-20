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

app.include_router(collection_cards.router)

app.include_router(cards.router)

app.include_router(sets.router)

app.include_router(collections.router)