import logging
from datetime import UTC, datetime

from sqlalchemy import exc as sqlalchemy_exc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from acesso_livre_api.src.comments import models, schemas

from acesso_livre_api.src.locations.service import update_location_average_rating
from acesso_livre_api.src.comments.exceptions import (
    CommentCreateException,
    CommentDeleteException,
    CommentGenericException,
    CommentImagesInvalidException,
    CommentNotFoundException,
    CommentNotPendingException,
    CommentPermissionDeniedException,
    CommentRatingInvalidException,
    CommentStatusInvalidException,
    CommentUpdateException,
)
from acesso_livre_api.storage import upload_image
from acesso_livre_api.storage.get_url import get_signed_urls
from fastapi import UploadFile

from acesso_livre_api.src.locations import models as location_models

from func_log import *

logger = logging.getLogger(__name__)


async def get_comment(db: AsyncSession, comment_id: int):
    try:
        stmt = select(models.Comment).where(
            models.Comment.id == comment_id, models.Comment.status == "approved"
        )
        result = await db.execute(stmt)
        comment = result.scalar_one_or_none()

        if not comment:
            log_message(f"Comentário {comment_id} não encontrado", level="warning")
            raise CommentNotFoundException()

        if comment.images is None:
            comment.images = []
            log_message(f"Comentário {comment_id} não possui imagens", level="info")
        else:
            comment.images = await get_signed_urls(comment.images)
            log_message(f"Imagens do comentário {comment_id} processadas com sucesso", level="info")

        log_message(f"Comentário {comment_id} recuperado com sucesso", level="info")
        return comment

    except CommentNotFoundException:
        log_message(f"Comentário {comment_id} não encontrado", level="warning")
        raise
    except Exception as e:
        log_message(f"Erro ao obter comentário {comment_id}: {str(e)}", level="error")
        log_message(str(e), level="error")
        logger.error("Erro ao obter comentário %s: %s", comment_id, str(e))
        raise CommentNotFoundException()


async def create_comment(
    db: AsyncSession,
    comment: schemas.CommentCreate,
    images: list[UploadFile] | None = None,
):
    try:
        if comment.rating < 1 or comment.rating > 5:
            log_message(f"Avaliação inválida fornecida: {comment.rating}", level="warning")
            raise CommentRatingInvalidException(comment.rating)

        image_list = []
        if images:
            for img in images:
                upload_image_path = await upload_image.upload_image(img)
                image_list.append(upload_image_path)

        data = comment.model_dump()
        data["images"] = image_list

        db_comment = models.Comment(**data, created_at=datetime.now(UTC))
        db.add(db_comment)
        await db.commit()
        await db.refresh(db_comment)

        log_message(f"Comentário criado com sucesso para o local {comment.location_id} por {comment.user_name}", level="info")
        return db_comment

    except (CommentRatingInvalidException, CommentImagesInvalidException):
        log_message(f"Falha ao criar comentário para o local {comment.location_id} por {comment.user_name}", level="warning")
        raise
    except Exception as e:
        log_message(f"Erro ao criar comentário para o local {comment.location_id} por {comment.user_name}", level="error")
        log_message(str(e), level="error")
        logger.error("Erro ao criar comentário: %s", str(e))
        await db.rollback()
        raise CommentCreateException()


async def get_comments_with_status_pending(
    db: AsyncSession, skip: int = 0, limit: int = 10
):
    try:
        stmt = (
            select(models.Comment)
            .where(models.Comment.status == "pending")
            .order_by(models.Comment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        comments = result.scalars().all()

        if not comments:
            log_message("Nenhum comentário pendente encontrado", level="info")
            return []

        for comment in comments:
            if comment.images is None:
                log_message(f"Comentário {comment.id} não possui imagens", level="info")
                comment.images = []
            else:
                log_message(f"Processando imagens do comentário {comment.id}", level="info")
                comment.images = await get_signed_urls(comment.images)

        log_message(f"Recuperados {len(comments)} comentários pendentes", level="info")
        return comments

    except Exception as e:
        logger.error("Erro ao buscar comentários pendentes: %s", str(e))
        log_message("Erro ao buscar comentários pendentes", level="error")
        log_message(str(e), level="error")
        raise CommentGenericException()


async def update_comment_status(
    db: AsyncSession, comment_id: int, new_status: schemas.CommentUpdateStatus
):
    try:
        logger.info(
            "Tentando atualizar comentário %s para status %s",
            comment_id,
            new_status.status.value,
        )

        # Compute the status value and log the intent separately to avoid a malformed expression.
        status_value = (
            new_status.status.value
            if hasattr(new_status.status, "value")
            else new_status.status
        )
        log_message(f"Atualizando status para {status_value}", level="info")
        if status_value not in ["approved", "rejected"]:
            log_message(f"Status inválido fornecido: {status_value}", level="warning")
            raise CommentStatusInvalidException(status_value)

        stmt = select(models.Comment).where(models.Comment.id == comment_id)
        result = await db.execute(stmt)
        comment = result.scalar_one_or_none()
        logger.info("Comentário encontrado: %s", comment is not None)

        if not comment:
            log_message(f"Comentário {comment_id} não encontrado", level="warning")
            raise CommentNotFoundException()

        logger.info("Status atual do comentário: %s", comment.status)
        if comment.status != "pending":
            log_message(f"Comentário {comment_id} não está pendente (status atual: {comment.status})", level="warning")
            raise CommentNotPendingException(comment_id, comment.status)

        comment.status = status_value
        await db.commit()
        await db.refresh(comment)

        if status_value == "approved":
            await update_location_average_rating(db, comment.location_id, comment.rating)

            if comment.images and len(comment.images) > 0:
                stmt_location = select(location_models.Location).where(
                    location_models.Location.id == comment.location_id
                )
                result_location = await db.execute(stmt_location)
                location = result_location.scalar_one_or_none()

                if location:
                    if location.images is None:
                        location.images = []

                    for image_path in comment.images:
                        if image_path not in location.images:
                            location.images.append(image_path)

                await db.commit()

        if comment.images is None:
            comment.images = []
        log_message(f"Comentário {comment_id} atualizado com sucesso para status {status_value}", level="info")
        logger.info(
            "Comentário %s atualizado com sucesso para status %s",
            comment_id,
            status_value,
        )
        return comment

    except (
        CommentNotFoundException,
        CommentStatusInvalidException,
        CommentNotPendingException,
    ):
        log_message(f"Falha ao atualizar status do comentário {comment_id}", level="warning")
        raise
    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error(
            "Erro de banco de dados ao atualizar comentário %s: %s", comment_id, str(e)
        )
        log_message(f"Erro de banco de dados ao atualizar comentário {comment_id}", level="error")
        await db.rollback()
        raise CommentUpdateException()
    except Exception as e:
        log_message(f"Erro inesperado ao atualizar comentário {comment_id}", level="error")
        log_message(str(e), level="error")
        logger.error("Erro inesperado ao atualizar comentário %s: %s", comment_id, str(e))
        await db.rollback()
        raise CommentUpdateException()


async def delete_comment(
    db: AsyncSession, comment_id: int, user_permissions: bool = True
):
    try:
        if not user_permissions:
            raise CommentPermissionDeniedException("excluir")

        stmt = select(models.Comment).where(models.Comment.id == comment_id)
        result = await db.execute(stmt)
        comment = result.scalar_one_or_none()

        if not comment:
            raise CommentNotFoundException()

        await db.delete(comment)
        await db.commit()

        log_message(f"Comentário {comment_id} excluído com sucesso", level="info")
        return True

    except (CommentNotFoundException, CommentPermissionDeniedException):
        log_message(f"Falha ao excluir comentário {comment_id}", level="warning")
        raise
    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error(
            "Erro de banco de dados ao excluir comentário %s: %s", comment_id, str(e)
        )
        await db.rollback()
        log_message(f"Erro de banco de dados ao excluir comentário {comment_id}", level="error")    
        raise CommentDeleteException()
    except Exception as e:
        logger.error("Erro inesperado ao excluir comentário %s: %s", comment_id, str(e))
        await db.rollback()
        log_message(f"Erro inesperado ao excluir comentário {comment_id}", level="error")  
        raise CommentDeleteException()


async def get_all_comments_by_location_id(
    location_id: int, skip: int, limit: int, db: AsyncSession
):
    try:
        stmt = (
            select(models.Comment)
            .where(
                models.Comment.location_id == location_id,
                models.Comment.status == "approved",
            )
            .order_by(models.Comment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        comments = result.scalars().all()

        if not comments:
            return []

        for comment in comments:
            if comment.images is None:
                comment.images = []
            else:
                comment.images = await get_signed_urls(comment.images)

        log_message(f"Recuperados {len(comments)} comentários para o local {location_id}", level="info")
        return comments

    except Exception as e:
        log_message(f"Erro ao buscar comentários para o local {location_id}", level="error")
        log_message(str(e), level="error")
        logger.error(
            "Erro ao buscar comentários para o local %s: %s", location_id, str(e)
        )
        raise CommentGenericException()


async def get_recent_comments(db: AsyncSession, limit: int = 3):
    try:
        stmt = (
            select(models.Comment)
            .options(selectinload(models.Comment.location))
            .where(models.Comment.status == "approved")
            .order_by(models.Comment.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        comments = result.unique().scalars().all()

        if not comments:
            return []

        log_message(f"Recuperados {len(comments)} comentários recentes", level="info")
        return comments

    except Exception as e:
        log_message("Erro ao recuperar comentários recentes", level="error")
        log_message(str(e), level="error")
        logger.error("Erro ao buscar comentários recentes: %s", str(e))
        raise CommentGenericException()
