from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from acesso_livre_api.src.admins import dependencies
from acesso_livre_api.src.database import get_db
from acesso_livre_api.src.locations import docs, schemas, service

router = APIRouter()


@router.post(
    "/", response_model=schemas.LocationCreateResponse, **docs.CREATE_LOCATION_DOCS
)
@dependencies.require_auth
def create_location(
    location: schemas.LocationCreate,
    authenticated_user: bool = dependencies.authenticated_user,
    db: Session = Depends(get_db),
):
    location = service.create_location(location=location, db=db)
    return location


@router.post(
    "/accessibility-items/",
    response_model=schemas.AccessibilityItemResponse,
    **docs.CREATE_ACCESSIBILITY_ITEM_DOCS,
)
@dependencies.require_auth
def create_accessibility_item(
    item: schemas.AccessibilityItemCreate,
    authenticated_user: bool = dependencies.authenticated_user,
    db: Session = Depends(get_db),
):
    db_item = service.create_accessibility_item(db=db, item=item)
    return db_item


@router.get(
    "/accessibility-items/",
    response_model=schemas.AccessibilityItemResponseList,
    **docs.LIST_ACCESSIBILITY_ITEMS_DOCS,
)
def get_accessibility_items(db: Session = Depends(get_db)):
    items = service.get_all_accessibility_items(db=db)
    return items


@router.get(
    "/accessibility-items/{item_id}",
    response_model=schemas.AccessibilityItemResponse,
    **docs.GET_ACCESSIBILITY_ITEM_DOCS,
)
def get_accessibility_item_by_id(
    item_id: int = Path(..., gt=0), db: Session = Depends(get_db)
):
    item = service.get_accessibility_item_by_id(db=db, item_id=item_id)
    return item


@router.get("/", response_model=schemas.LocationListResponse, **docs.LIST_LOCATIONS_DOCS)
def list_all_locations(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(
        20, ge=1, le=100, description="Número máximo de registros a retornar"
    ),
    db: Session = Depends(get_db),
):
    locations = service.get_all_locations(db=db, skip=skip, limit=limit)
    return schemas.LocationListResponse(locations=locations)


@router.get(
    "/{location_id}",
    response_model=schemas.LocationDetailResponse,
    **docs.GET_LOCATION_DOCS,
)
def get_location_by_id(location_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    location = service.get_location_by_id(db=db, location_id=location_id)
    return location


@router.patch(
    "/{location_id}",
    response_model=schemas.LocationDetailResponse,
    **docs.UPDATE_LOCATION_DOCS,
)
@dependencies.require_auth
def update_location(
    location_update: schemas.LocationUpdate,
    location_id: int = Path(..., gt=0),
    authenticated_user: bool = dependencies.authenticated_user,
    db: Session = Depends(get_db),
):
    location = service.update_location(
        db=db, location_id=location_id, location_update=location_update
    )
    return location


@router.delete(
    "/{location_id}",
    response_model=schemas.LocationDeleteResponse,
    **docs.DELETE_LOCATION_DOCS,
)
@dependencies.require_auth
def delete_location(
    location_id: int = Path(..., gt=0),
    authenticated_user: bool = dependencies.authenticated_user,
    db: Session = Depends(get_db),
):
    result = service.delete_location(db=db, location_id=location_id)
    return result
