from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class CollectionCard(Base):
    __tablename__ = "collection_cards"

    id = Column(Integer, primary_key=True, index=True)

    collection_id = Column(
        Integer,

        ForeignKey(
            "collections.id",
            ondelete="CASCADE"
        ),

        nullable=False
    )

    card_id = Column(Integer, ForeignKey("cards.id"),nullable=False)

    quantity = Column(Integer, default=1, nullable=False)

    is_commander = Column(Boolean, default=False)

    collection = relationship("Collection", back_populates="cards")

    card = relationship("Card", back_populates="collection_cards")


    # Evitar duplicados de cartas
    __table_args__ = (  
        UniqueConstraint("collection_id", "card_id"),
    )

