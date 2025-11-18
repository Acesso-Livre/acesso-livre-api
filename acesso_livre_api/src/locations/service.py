import logging

from sqlalchemy import exc as sqlalchemy_exc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from acesso_livre_api.src.comments import models as comment_models
from acesso_livre_api.src.locations import exceptions, models, schemas
from acesso_livre_api.storage.get_url import get_signed_url, get_signed_urls

logger = logging.getLogger(__name__)


async def create_location(db: AsyncSession, location: schemas.LocationCreate):
    try:
        data = location.model_dump()

        db_location = models.Location(**data)
        db.add(db_location)
        await db.commit()
        await db.refresh(db_location)

        return db_location

    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error(f"Erro de banco de dados ao criar localização: {str(e)}")
        await db.rollback()
        raise exceptions.LocationCreateException()
    except Exception as e:
        logger.error(f"Erro inesperado ao criar localização: {str(e)}")
        await db.rollback()
        raise exceptions.LocationCreateException()


async def get_all_locations(db: AsyncSession, skip: int = 0, limit: int = 20):
    try:
        stmt = select(models.Location).offset(skip).limit(limit)
        result = await db.execute(stmt)
        locations = result.scalars().all()
        return locations

    except Exception as e:
        logger.error(f"Erro ao obter localizações: {str(e)}")
        raise exceptions.LocationGenericException()


async def create_accessibility_item(
    db: AsyncSession, item: schemas.AccessibilityItemCreate
):
    try:
        data = item.model_dump()
        db_item = models.AccessibilityItem(**data)
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item

    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error("Erro de banco de dados ao criar item de acessibilidade: %s", str(e))
        await db.rollback()
        raise exceptions.LocationGenericException()
    except Exception as e:
        logger.error("Erro inesperado ao criar item de acessibilidade: %s", str(e))
        await db.rollback()
        raise exceptions.LocationGenericException()


async def get_all_accessibility_items(db: AsyncSession):
    try:
        stmt = select(models.AccessibilityItem)
        result = await db.execute(stmt)
        items = result.scalars().all()

        icon_urls = [item.icon_url for item in items if item.icon_url]
        get_signed_urls_list = await get_signed_urls(icon_urls)

        return schemas.AccessibilityItemResponseList(
            accessibility_items=get_signed_urls_list
        )

    except Exception as e:
        logger.error("Erro ao obter itens de acessibilidade: %s", str(e))
        raise exceptions.LocationGenericException()


async def get_accessibility_item_by_id(db: AsyncSession, item_id: int):
    try:
        stmt = select(models.AccessibilityItem).where(
            models.AccessibilityItem.id == item_id
        )
        result = await db.execute(stmt)
        item = result.scalar_one_or_none()

        if not item:
            raise exceptions.LocationNotFoundException()

        image_url = await get_signed_url(item.icon_url) if item.icon_url else None
        return schemas.AccessibilityItemResponse(
            id=item.id, name=item.name, icon_url=image_url
        )

    except Exception as e:
        logger.error("Erro ao obter item de acessibilidade %s: %s", item_id, str(e))
        raise exceptions.LocationGenericException()


async def get_location_by_id(db: AsyncSession, location_id: int):
    try:
        stmt = (
            select(models.Location)
            .options(selectinload(models.Location.accessibility_items))
            .where(models.Location.id == location_id)
        )
        result = await db.execute(stmt)
        location = result.unique().scalar_one_or_none()

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
        logger.error("Erro ao obter localização %s: %s", location_id, str(e))
        raise exceptions.LocationNotFoundException()


async def update_location(
    db: AsyncSession, location_id: int, location_update: schemas.LocationUpdate
):
    try:
        stmt = (
            select(models.Location)
            .options(selectinload(models.Location.accessibility_items))
            .where(models.Location.id == location_id)
        )
        result = await db.execute(stmt)
        location = result.unique().scalar_one_or_none()

        if not location:
            raise exceptions.LocationNotFoundException()

        update_data = location_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(location, field, value)
        await db.commit()
        await db.refresh(location)

        if location.images is None:
            location.images = []
        if location.avg_rating is None:
            location.avg_rating = 0.0

        return location

    except exceptions.LocationNotFoundException:
        raise
    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error(
            "Erro de banco de dados ao atualizar localização %s: %s", location_id, str(e)
        )
        await db.rollback()
        raise exceptions.LocationUpdateException()
    except Exception as e:
        logger.error(
            "Erro inesperado ao atualizar localização %s: %s", location_id, str(e)
        )
        await db.rollback()
        raise exceptions.LocationUpdateException()


async def delete_location(db: AsyncSession, location_id: int):
    try:
        stmt = (
            select(models.Location)
            .options(selectinload(models.Location.accessibility_items))
            .where(models.Location.id == location_id)
        )
        result = await db.execute(stmt)
        location = result.unique().scalar_one_or_none()

        if not location:
            raise exceptions.LocationNotFoundException()

        await db.delete(location)
        await db.commit()
        return True

    except exceptions.LocationNotFoundException:
        raise
    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error(
            "Erro de banco de dados ao excluir localização %s: %s", location_id, str(e)
        )
        await db.rollback()
        raise exceptions.LocationDeleteException()
    except Exception as e:
        logger.error("Erro inesperado ao excluir localização %s: %s", location_id, str(e))
        await db.rollback()
        raise exceptions.LocationDeleteException()


async def update_location_average_rating(
    db: AsyncSession, location_id: int, new_value: float
):
    try:
        stmt = select(models.Location).where(models.Location.id == location_id)
        result = await db.execute(stmt)
        location = result.scalar_one_or_none()

        if not location:
            return

        stmt_count = select(comment_models.Comment).where(
            comment_models.Comment.location_id == location_id,
            comment_models.Comment.status == "approved",
        )
        result_count = await db.execute(stmt_count)
        count_approved = len(result_count.scalars().all())

        current_avg = location.avg_rating or 0.0

        count_previous = count_approved - 1

        location.avg_rating = ((current_avg * count_previous) + new_value) / (
            count_approved
        )

        await db.commit()
        await db.refresh(location)
        return location
    except exceptions.LocationNotFoundException:
        raise
    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error(
            "Erro de banco de dados ao atualizar média de avaliação da localização %s: %s",
            location_id,
            str(e),
        )
        await db.rollback()
        raise exceptions.LocationUpdateException()
    except Exception as e:
        logger.error(
            "Erro inesperado ao atualizar média de avaliação da localização %s: %s",
            location_id,
            str(e),
        )
        await db.rollback()
        raise exceptions.LocationUpdateException()
