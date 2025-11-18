import logging
from fastapi.concurrency import run_in_threadpool

from sqlalchemy import exc as sqlalchemy_exc
from sqlalchemy.orm import Session, joinedload
from acesso_livre_api.src.comments import models as comment_models
from acesso_livre_api.src.locations import exceptions, models, schemas
from acesso_livre_api.storage.get_url import get_signed_url, get_signed_urls

logger = logging.getLogger(__name__)


async def create_location(db: Session, location: schemas.LocationCreate):
    def _sync_create_location():
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

    return await run_in_threadpool(_sync_create_location)


async def get_all_locations(db: Session, skip: int = 0, limit: int = 20):
    def _sync_get_all_locations():
        try:
            locations = db.query(models.Location).offset(skip).limit(limit).all()
            return locations

        except Exception as e:
            logger.error(f"Erro ao obter localizações: {str(e)}")
            raise exceptions.LocationGenericException()

    return await run_in_threadpool(_sync_get_all_locations)


async def create_accessibility_item(db: Session, item: schemas.AccessibilityItemCreate):
    def _sync_create_accessibility_item():
        try:
            data = item.model_dump()
            db_item = models.AccessibilityItem(**data)
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
            return db_item

        except sqlalchemy_exc.SQLAlchemyError as e:
            logger.error(
                f"Erro de banco de dados ao criar item de acessibilidade: {str(e)}"
            )
            db.rollback()
            raise exceptions.LocationGenericException()
        except Exception as e:
            logger.error(f"Erro inesperado ao criar item de acessibilidade: {str(e)}")
            db.rollback()
            raise exceptions.LocationGenericException()

    return await run_in_threadpool(_sync_create_accessibility_item)


async def get_all_accessibility_items(db: Session):
    try:
        items = await run_in_threadpool(lambda: db.query(models.AccessibilityItem).all())

        icon_urls = [item.icon_url for item in items if item.icon_url]
        get_signed_urls_list = await get_signed_urls(icon_urls)

        return schemas.AccessibilityItemResponseList(
            accessibility_items=get_signed_urls_list
        )

    except Exception as e:
        logger.error(f"Erro ao obter itens de acessibilidade: {str(e)}")
        raise exceptions.LocationGenericException()


async def get_accessibility_item_by_id(db: Session, item_id: int):
    try:
        item = await run_in_threadpool(
            lambda: db.query(models.AccessibilityItem)
            .filter(models.AccessibilityItem.id == item_id)
            .first()
        )

        if not item:
            raise exceptions.LocationNotFoundException()

        image_url = await get_signed_url(item.icon_url) if item.icon_url else None
        return schemas.AccessibilityItemResponse(
            id=item.id, name=item.name, icon_url=image_url
        )

    except Exception as e:
        logger.error(f"Erro ao obter item de acessibilidade {item_id}: {str(e)}")
        raise exceptions.LocationGenericException()


async def get_location_by_id(db: Session, location_id: int):
    try:
        location = await run_in_threadpool(
            lambda: db.query(models.Location)
            .options(joinedload(models.Location.accessibility_items))
            .filter(models.Location.id == location_id)
            .first()
        )

        if not location:
            raise exceptions.LocationNotFoundException()

        if location.images is None:
            location.images = []
        else:
            location.images = await get_signed_urls(location.images)

        if location.avg_rating is None:
            location.avg_rating = 0.0

        return location

    except exceptions.LocationNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter localização {location_id}: {str(e)}")
        raise exceptions.LocationNotFoundException()


async def update_location(
    db: Session, location_id: int, location_update: schemas.LocationUpdate
):
    def _sync_update_location():
        try:
            location = (
                db.query(models.Location)
                .options(joinedload(models.Location.accessibility_items))
                .filter(models.Location.id == location_id)
                .first()
            )

            if not location:
                raise exceptions.LocationNotFoundException()

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
            logger.error(
                f"Erro de banco de dados ao atualizar localização {location_id}: {str(e)}"
            )
            db.rollback()
            raise exceptions.LocationUpdateException()
        except Exception as e:
            logger.error(
                f"Erro inesperado ao atualizar localização {location_id}: {str(e)}"
            )
            db.rollback()
            raise exceptions.LocationUpdateException()

    return await run_in_threadpool(_sync_update_location)


async def delete_location(db: Session, location_id: int):
    def _sync_delete_location():
        try:
            location = (
                db.query(models.Location)
                .options(joinedload(models.Location.accessibility_items))
                .filter(models.Location.id == location_id)
                .first()
            )

            if not location:
                raise exceptions.LocationNotFoundException()

            db.delete(location)
            db.commit()
            return True

        except exceptions.LocationNotFoundException:
            raise
        except sqlalchemy_exc.SQLAlchemyError as e:
            logger.error(
                f"Erro de banco de dados ao excluir localização {location_id}: {str(e)}"
            )
            db.rollback()
            raise exceptions.LocationDeleteException()
        except Exception as e:
            logger.error(
                f"Erro inesperado ao excluir localização {location_id}: {str(e)}"
            )
            db.rollback()
            raise exceptions.LocationDeleteException()

    return await run_in_threadpool(_sync_delete_location)


async def update_location_average_rating(db: Session, location_id: int, new_value: float):
    def _sync_update_location_average_rating():
        try:
            location = (
                db.query(models.Location)
                .filter(models.Location.id == location_id)
                .first()
            )

            if not location:
                return

            count_approved = (
                db.query(comment_models.Comment)
                .filter(
                    comment_models.Comment.location_id == location_id,
                    comment_models.Comment.status == "approved",
                )
                .count()
            )
            current_avg = location.avg_rating or 0.0

            count_previous = count_approved - 1

            location.avg_rating = ((current_avg * count_previous) + new_value) / (
                count_approved
            )

            db.commit()
            db.refresh(location)
            return location
        except exceptions.LocationNotFoundException:
            raise
        except sqlalchemy_exc.SQLAlchemyError as e:
            logger.error(
                f"Erro de banco de dados ao atualizar média de avaliação da localização {location_id}: {str(e)}"
            )
            db.rollback()
            raise exceptions.LocationUpdateException()
        except Exception as e:
            logger.error(
                f"Erro inesperado ao atualizar média de avaliação da localização {location_id}: {str(e)}"
            )
            db.rollback()
            raise exceptions.LocationUpdateException()

    return await run_in_threadpool(_sync_update_location_average_rating)
