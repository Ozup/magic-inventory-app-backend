from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Enum,
    UniqueConstraint
)

from sqlalchemy.orm import relationship

from database import Base

from datetime import datetime

import enum


####################################
# Collection Types
####################################

class CollectionType(enum.Enum):

    ALBUM = "ALBUM"

    DECK = "DECK"

    BINDER = "BINDER"

    COLLECTION = "COLLECTION"


####################################
# Deck Formats
####################################

class DeckFormat(enum.Enum):

    COMMANDER = "COMMANDER"

    STANDARD = "STANDARD"

    MODERN = "MODERN"

    PAUPER = "PAUPER"