from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

####################################
# Para el tipo de la colección debo restrigir las posibilidades.
####################################
import enum

class CollectionType(enum.Enum):
    ALBUM = "ALBUM"
    DECK = "DECK"
    BINDER = "BINDER"
####################################

class DeckFormat(enum.Enum):
    COMMANDER = "COMMANDER"
    STANDARD = "STANDARD"
    MODERN = "MODERN"
    PAUPER = "PAUPER"