from sqlalchemy import Column, Integer, String, Text, DateTime, CheckConstraint
from ..database import Base

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
    location_id = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False) 
    images = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)