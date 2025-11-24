from fastapi import APIRouter, Depends, Path, Query, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession

from acesso_livre_api.src.admins import dependencies
from acesso_livre_api.src.database import get_db
from acesso_livre_api.src.locations import docs, schemas, service
from acesso_livre_api.storage import upload_image

router = APIRouter()


@router.post(
    "/", response_model=schemas.LocationCreateResponse, **docs.CREATE_LOCATION_DOCS
)
@dependencies.require_auth
async def create_location(
    location: schemas.LocationCreate,
    authenticated_user: bool = dependencies.authenticated_user,
    db: AsyncSession = Depends(get_db),
):
    location = await service.create_location(db=db, location=location)
    return location


@router.post(
    "/accessibility-items/",
    response_model=schemas.AccessibilityItemCreateResponse,
    **docs.CREATE_ACCESSIBILITY_ITEM_DOCS,
)
@dependencies.require_auth
async def create_accessibility_item(
    name: str = Form(...),
    image: UploadFile = File(...),
    authenticated_user: bool = dependencies.authenticated_user,
    db: AsyncSession = Depends(get_db),
):
    # Fazer upload para o storage
    icon_url = await upload_image.upload_image(image)

    # Criar o item com o path
    item_data = schemas.AccessibilityItemCreate(name=name, icon_url=icon_url)
    db_item = await service.create_accessibility_item(db=db, item=item_data)
    return db_item


@router.get(
    "/accessibility-items/",
    response_model=schemas.AccessibilityItemResponseList,
    **docs.LIST_ACCESSIBILITY_ITEMS_DOCS,
)
async def get_accessibility_items(db: AsyncSession = Depends(get_db)):
    items = await service.get_all_accessibility_items(db=db)
    return items


@router.get(
    "/accessibility-items/{item_id}",
    response_model=schemas.AccessibilityItemResponse,
    **docs.GET_ACCESSIBILITY_ITEM_DOCS,
)
async def get_accessibility_item_by_id(
    item_id: int = Path(..., gt=0), db: AsyncSession = Depends(get_db)
):
    item = await service.get_accessibility_item_by_id(db=db, item_id=item_id)
    return item


@router.get("/", response_model=schemas.LocationListResponse, **docs.LIST_LOCATIONS_DOCS)
async def list_all_locations(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(
        20, ge=1, le=100, description="Número máximo de registros a retornar"
    ),
    db: AsyncSession = Depends(get_db),
):
    locations = await service.get_all_locations(db=db, skip=skip, limit=limit)
    return schemas.LocationListResponse(locations=locations)


@router.get(
    "/{location_id}",
    response_model=schemas.LocationDetailResponse,
    **docs.GET_LOCATION_DOCS,
)
async def get_location_by_id(
    location_id: int = Path(..., gt=0),
    skip: int = Query(
        0,
        ge=0,
        description="Número de comentários a pular (não retornado, usado apenas para consolidar imagens)",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Número máximo de comentários a considerar para consolidar imagens",
    ),
    db: AsyncSession = Depends(get_db),
):
    location = await service.get_location_by_id(
        db=db, location_id=location_id, skip=skip, limit=limit
    )
    return location


@router.patch(
    "/{location_id}",
    response_model=schemas.LocationDetailResponse,
    **docs.UPDATE_LOCATION_DOCS,
)
@dependencies.require_auth
async def update_location(
    location_update: schemas.LocationUpdate,
    location_id: int = Path(..., gt=0),
    authenticated_user: bool = dependencies.authenticated_user,
    db: AsyncSession = Depends(get_db),
):
    location = await service.update_location(
        db=db, location_id=location_id, location_update=location_update
    )
    return location


@router.delete(
    "/{location_id}",
    response_model=schemas.LocationDeleteResponse,
    **docs.DELETE_LOCATION_DOCS,
)
@dependencies.require_auth
async def delete_location(
    location_id: int = Path(..., gt=0),
    authenticated_user: bool = dependencies.authenticated_user,
    db: AsyncSession = Depends(get_db),
):
    result = await service.delete_location(db=db, location_id=location_id)
    return result
