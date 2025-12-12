from enum import Enum
import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from ..database import Base


class CommentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved" 
    REJECTED = "rejected"


# Tabela associativa para relacionamento many-to-many entre Comment e CommentIcon
comment_comment_icons_association = Table(
    "comment_comment_icons",
    Base.metadata,
    Column("comment_id", Integer, ForeignKey("comments.id"), primary_key=True),
    Column("icon_id", Integer, ForeignKey("comment_icons.id"), primary_key=True),
)


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
    
    # Relacionamento many-to-many com CommentIcon
    comment_icons = relationship(
        "CommentIcon",
        secondary=comment_comment_icons_association,
        back_populates="comments",
    )


class CommentIcon(Base):
    __tablename__ = "comment_icons"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    icon_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # Relacionamento many-to-many com Comment
    comments = relationship(
        "Comment",
        secondary=comment_comment_icons_association,
        back_populates="comment_icons",
    )