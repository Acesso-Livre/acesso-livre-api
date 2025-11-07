import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from ..database import Base

# Tabela associativa para relacionamento many-to-many entre Location e AccessibilityItem
location_accessibility_association = Table(
    'location_accessibility',
    Base.metadata,
    Column('location_id', Integer, ForeignKey('locations.id'), primary_key=True),
    Column('item_id', Integer, ForeignKey('accessibility_items.id'), primary_key=True)
)

class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    images = Column(JSON, nullable=True)
    avg_rating = Column(Float, default=0.0, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relacionamento many-to-many com AccessibilityItem
    accessibility_items = relationship(
        'AccessibilityItem',
        secondary=location_accessibility_association,
        back_populates='locations'
    )

    # Relacionamento one-to-many com Comments
    comments = relationship('Comment', back_populates='location')

class AccessibilityItem(Base):
    __tablename__ = 'accessibility_items'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    icon_url = Column(String)
    top = Column(Float, nullable=False)
    left = Column(Float, nullable=False)

    # Relacionamento many-to-many com Location
    locations = relationship(
        'Location',
        secondary=location_accessibility_association,
        back_populates='accessibility_items'
    )