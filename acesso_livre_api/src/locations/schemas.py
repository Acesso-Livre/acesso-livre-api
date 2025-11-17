from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field

from acesso_livre_api.storage.get_url import get_public_url


class LocationBase(BaseModel):
    """Schema base para Location com campos comuns."""

    id: int
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)

    model_config = ConfigDict(from_attributes=True)


class LocationCreate(BaseModel):
    """Schema para criação de Location."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str
    top: float
    left: float

    model_config = ConfigDict(from_attributes=True)


class LocationCreateResponse(BaseModel):
    """Schema para resposta de criação de Location."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class LocationUpdate(BaseModel):
    """Schema para atualização de Location."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AccessibilityItemCreate(BaseModel):
    """Schema para criação de itens de acessibilidade."""

    name: str
    icon_path: str

    model_config = ConfigDict(from_attributes=True)


class AccessibilityItemResponse(BaseModel):
    """Schema para resposta de itens de acessibilidade."""

    id: int
    name: str
    icon_url: str

    model_config = ConfigDict(from_attributes=True)


class AccessibilityItemCreateResponse(BaseModel):
    """Schema para resposta de criação de item de acessibilidade (sem URL)."""

    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class AccessibilityItemResponseList(BaseModel):
    """Schema para lista de itens de acessibilidade."""

    accessibility_items: List[AccessibilityItemResponse] = Field(default=[])

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


class LocationDeleteResponse(BaseModel):
    """Schema para resposta de exclusão de Location."""

    message: str

    model_config = ConfigDict(from_attributes=True)
