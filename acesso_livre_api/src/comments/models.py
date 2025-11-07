from enum import Enum

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from ..database import Base


class CommentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved" 
    REJECTED = "rejected"

class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='rating_range'),
        CheckConstraint('status IN (\'pending\', \'approved\', \'rejected\')', name='status_values'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(255), index=True, nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=True)
    status = Column(String(50), nullable=False, default=CommentStatus.PENDING)
    images = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)

    # Relacionamento com Location
    location = relationship('Location', back_populates='comments')