from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import List, Optional

class CommentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved" 
    REJECTED = "rejected"

class CommentCreate(BaseModel):
    user_name: str = Field(..., max_length=30)
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., max_length=500)
    images: Optional[List[str]] = None

class CommentCreateResponse(BaseModel):
    id: int
    status: CommentStatus

class CommentUpdateStatus(BaseModel):
    status: CommentStatus

class CommentResponseWithLocationId(BaseModel):
    id: int
    user_name: str
    rating: int
    comment: str
    images: List[str]
    created_at: datetime

class CommentResponseOnlyStatusPending(BaseModel):
    id: int
    user_name: str
    rating: int
    comment: str
    location_id: Optional[int] = None
    status: CommentStatus
    images: List[str]
    created_at: datetime

    class Config:
        from_attributes = True

class CommentListResponse(BaseModel):
    comments: List[CommentResponseOnlyStatusPending]

    class Config:
        from_attributes = True