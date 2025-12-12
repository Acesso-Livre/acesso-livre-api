from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field, ConfigDict
from acesso_livre_api.src.locations.schemas import ImageResponse


class CommentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class CommentIconResponse(BaseModel):
    """Schema para resposta de ícones de comentário."""
    id: int
    name: str
    icon_url: str

    model_config = ConfigDict(from_attributes=True)


class CommentIconCreateResponse(BaseModel):
    """Schema para resposta de criação de ícone de comentário."""
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    user_name: str = Field(..., max_length=30)
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., max_length=500)
    location_id: int
    comment_icon_ids: Optional[List[int]] = Field(default=None)


class CommentCreateImages(BaseModel):
    images: List[str]


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
    location_id: int


class CommentResponseOnlyStatusPending(BaseModel):
    id: int
    user_name: str
    rating: int
    comment: str
    location_id: int
    status: CommentStatus
    images: List[ImageResponse]
    created_at: datetime
    comment_icons: List[CommentIconResponse] = Field(default=[])

    model_config = ConfigDict(from_attributes=True)


class CommentListResponse(BaseModel):
    comments: List[CommentResponseOnlyStatusPending]

    model_config = ConfigDict(from_attributes=True)


class CommentResponse(BaseModel):
    id: int
    user_name: str
    rating: int
    comment: str
    location_id: int
    status: CommentStatus
    images: List[ImageResponse]
    created_at: datetime
    comment_icons: List[CommentIconResponse] = Field(default=[])

    model_config = ConfigDict(from_attributes=True)


class CommentListByLocationResponse(BaseModel):
    comments: List[CommentResponse]

    model_config = ConfigDict(from_attributes=True)


class RecentCommentResponse(BaseModel):
    location_name: str
    location_rating: float
    user_name: str
    description: str

    model_config = ConfigDict(from_attributes=True)

class RecentCommentsListResponse(BaseModel):
    comments: List[RecentCommentResponse]

    class Config:
        from_attributes = True
