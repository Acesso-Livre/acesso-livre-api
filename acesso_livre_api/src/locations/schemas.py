from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class LocationBase(BaseModel):
    """Schema base para Location com campos comuns."""
    id: int
    name: str = Field(..., min_length=1, max_length=200)
    description: str

    model_config = ConfigDict(from_attributes=True)


class AccessibilityItemResponse(BaseModel):
    """Schema para resposta de itens de acessibilidade."""
    id: int
    name: str
    icon_url: str

    model_config = ConfigDict(from_attributes=True)


class LocationListResponse(BaseModel):
    """Schema para resposta da listagem de locations (GET /locations)."""
    locations: List[LocationBase] = Field(default=[])

    model_config = ConfigDict(from_attributes=True)


class LocationDetailResponse(LocationBase):
    """Schema para resposta dos detalhes de um location específico (GET /locations/{id})."""
    images: List[str] = Field(default=[])
    avg_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    accessibility_items: List[AccessibilityItemResponse] = Field(default=[])


class LocationsQueryParams(BaseModel):
    """Schema para query parameters da listagem de locations."""
    filter: Optional[str] = Field(None, min_length=1, max_length=100)

    model_config = ConfigDict(extra="forbid")