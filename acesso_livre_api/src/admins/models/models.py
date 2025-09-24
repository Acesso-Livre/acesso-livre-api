from sqlalchemy import Column, Integer, String, Text, DateTime, func
from ...database import Base

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(256), nullable=False, unique=True)
    password = Column(Text, nullable=False)
    reset_token_hash = Column(Text, nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())