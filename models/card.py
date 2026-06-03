from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from sqlalchemy import Float

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)

    scryfall_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    
    type_line = Column(String)
    rarity = Column(String)

    mana_cost = Column(String, nullable=True)
    image_url = Column(String, nullable=True)

    rarity = Column(String)

    set_name = Column(String, nullable=True)

    set_code = Column(String, nullable=True)

    collector_number = Column(String, nullable=True)

    oracle_text = Column(String, nullable=True) # Para filtrar cartas por efectos, etc...

    colors = Column(String, nullable=True)

    color_identity = Column(String, nullable=True)

    cmc = Column(Integer, nullable=True)
    usd_price = Column(Float, nullable=True)

    collection_cards = relationship("CollectionCard", back_populates="card")
  