import logging

from sqlalchemy import exc as sqlalchemy_exc
from sqlalchemy.orm import Session, joinedload

from acesso_livre_api.src.locations import exceptions, models, schemas

logger = logging.getLogger(__name__)

def create_location(db: Session, location: schemas.LocationCreate):
    try:
        data = location.model_dump()
        db_location = models.Location(**data)
        db.add(db_location)
        db.commit()
        db.refresh(db_location)

        return db_location

    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error(f"Erro de banco de dados ao criar localização: {str(e)}")
        db.rollback()
        raise exceptions.LocationCreateException()
    except Exception as e:
        logger.error(f"Erro inesperado ao criar localização: {str(e)}")
        db.rollback()
        raise exceptions.LocationCreateException()

def get_all_locations(db: Session, skip: int = 0, limit: int = 20):
    try:
        locations = db.query(models.Location).offset(skip).limit(limit).all()
        return locations

    except Exception as e:
        logger.error(f"Erro ao obter localizações: {str(e)}")
        raise exceptions.LocationGenericException()

def create_accessibility_item(db: Session, item: schemas.AccessibilityItemCreate):
    try:
        data = item.model_dump()
        db_item = models.AccessibilityItem(**data)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error(f"Erro de banco de dados ao criar item de acessibilidade: {str(e)}")
        db.rollback()
        raise exceptions.LocationGenericException()
    except Exception as e:
        logger.error(f"Erro inesperado ao criar item de acessibilidade: {str(e)}")
        db.rollback()
        raise exceptions.LocationGenericException()

def get_all_accessibility_items(db: Session):
    try:
        items = db.query(models.AccessibilityItem).all()
        return schemas.AccessibilityItemResponseList(accessibility_items=items)

    except Exception as e:
        logger.error(f"Erro ao obter itens de acessibilidade: {str(e)}")
        raise exceptions.LocationGenericException()

def get_accessibility_item_by_id(db: Session, item_id: int):
    try:
        item = db.query(models.AccessibilityItem).filter(models.AccessibilityItem.id == item_id).first()

        if not item:
            raise exceptions.LocationNotFoundException()

        return item

    except Exception as e:
        logger.error(f"Erro ao obter item de acessibilidade {item_id}: {str(e)}")
        raise exceptions.LocationGenericException()


def get_location_by_id(db: Session, location_id: int):
    try:
        location = db.query(models.Location).options(joinedload(models.Location.accessibility_items)).filter(models.Location.id == location_id).first()

        if not location:
            raise exceptions.LocationNotFoundException()

        if location.images is None:
            location.images = []
        if location.avg_rating is None:
            location.avg_rating = 0.0

        return location

    except exceptions.LocationNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter localização {location_id}: {str(e)}")
        raise exceptions.LocationNotFoundException()


def update_location(db: Session, location_id: int, location_update: schemas.LocationUpdate):
    try:
        location = get_location_by_id(db, location_id)
        update_data = location_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(location, field, value)
        db.commit()
        db.refresh(location)

        if location.images is None:
            location.images = []
        if location.avg_rating is None:
            location.avg_rating = 0.0

        return location

    except exceptions.LocationNotFoundException:
        raise
    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error(f"Erro de banco de dados ao atualizar localização {location_id}: {str(e)}")
        db.rollback()
        raise exceptions.LocationUpdateException()
    except Exception as e:
        logger.error(f"Erro inesperado ao atualizar localização {location_id}: {str(e)}")
        db.rollback()
        raise exceptions.LocationUpdateException()


def delete_location(db: Session, location_id: int):
    try:
        location = get_location_by_id(db, location_id)
        db.delete(location)
        db.commit()
        return True

    except exceptions.LocationNotFoundException:
        raise
    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error(f"Erro de banco de dados ao excluir localização {location_id}: {str(e)}")
        db.rollback()
        raise exceptions.LocationDeleteException()
    except Exception as e:
        logger.error(f"Erro inesperado ao excluir localização {location_id}: {str(e)}")
        db.rollback()
        raise exceptions.LocationDeleteException()