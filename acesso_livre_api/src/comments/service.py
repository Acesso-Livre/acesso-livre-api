import logging
from datetime import UTC, datetime
from collections.abc import Iterable

from sqlalchemy import exc as sqlalchemy_exc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from acesso_livre_api.src.comments import models, schemas
from acesso_livre_api.src.comments.utils import (
    extract_image_id,
    find_image_path_by_id,
    get_images_with_ids,
)

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
    ImageDeleteException,
    ImageNotFoundException,
)
from acesso_livre_api.storage import upload_image
from acesso_livre_api.storage.delete_image import delete_image, delete_images
from acesso_livre_api.storage.get_url import get_signed_url, get_signed_urls
from fastapi import UploadFile

from acesso_livre_api.src.locations import models as location_models

logger = logging.getLogger(__name__)

from ..func_log import log_message


def _safe_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, (tuple, set)):
        return list(value)
    if isinstance(value, (str, bytes)):
        return []
    try:
        if isinstance(value, Iterable):
            return list(value)
    except TypeError:
        return []
    return []


async def get_comment(db: AsyncSession, comment_id: int):
    try:
        stmt = (
            select(models.Comment)
            .options(selectinload(models.Comment.comment_icons))
            .where(models.Comment.id == comment_id, models.Comment.status == "approved")
        )
        result = await db.execute(stmt)
        comment = result.unique().scalars().first()

        if not comment:
            log_message(f"Comentário {comment_id} não encontrado", level="error", logger_name="acesso_livre_api")
            raise CommentNotFoundException()

        if comment.images is None:
            comment.images = []
        else:
            comment.images = await get_signed_urls(comment.images)

        # Processar ícones de comentário para obter signed URLs
        for icon in _safe_list(getattr(comment, "comment_icons", None)):
                if icon.icon_url:
                    signed_urls = await get_signed_urls([icon.icon_url])
                    if signed_urls:
                        icon.icon_url = signed_urls[0]

        log_message(f"Comentário {comment_id} recuperado com sucesso", level="info", logger_name="acesso_livre_api")
        return comment

    except CommentNotFoundException:
        log_message(f"Comentário {comment_id} não encontrado", level="error", logger_name="acesso_livre_api")
        raise
    except Exception as e:
        log_message(f"Erro ao obter comentário {comment_id}: {str(e)}", level="error", logger_name="acesso_livre_api")
        logger.error("Erro ao obter comentário %s: %s", comment_id, str(e))
        raise CommentNotFoundException()



async def create_comment(
    db: AsyncSession,
    comment: schemas.CommentCreate,
    images: list[UploadFile] | None = None,
):
    try:
        if comment.rating < 1 or comment.rating > 5:
            log_message(f"Avaliação inválida fornecida: {comment.rating}", level="error", logger_name="acesso_livre_api")
            raise CommentRatingInvalidException(comment.rating)

        image_list = []
        if images:
            for img in images:
                upload_image_path = await upload_image.upload_image(img)
                image_list.append(upload_image_path)

        data = comment.model_dump(exclude={"comment_icon_ids"})
        data["images"] = image_list

        db_comment = models.Comment(**data, created_at=datetime.now(UTC))
        db.add(db_comment)

        # Adicionar ícones de comentário se fornecidos
        if comment.comment_icon_ids:
            stmt = (
                select(models.CommentIcon)
                .where(models.CommentIcon.id.in_(comment.comment_icon_ids))
            )
            result = await db.execute(stmt)
            icons = result.scalars().all()
            
            for icon in icons:
                if icon not in db_comment.comment_icons:
                    db_comment.comment_icons.append(icon)

        await db.commit()
        await db.refresh(db_comment, attribute_names=["comment_icons"])

        log_message(f"Comentário criado com sucesso para localização {comment.location_id}", level="info", logger_name="acesso_livre_api")
        return db_comment

    except (CommentRatingInvalidException, CommentImagesInvalidException):
        log_message("Falha ao criar comentário devido a dados inválidos", level="error", logger_name="acesso_livre_api")
        raise
    except Exception as e:
        log_message(f"Erro ao criar comentário: {str(e)}", level="error", logger_name="acesso_livre_api")
        logger.error("Erro ao criar comentário: %s", str(e))
        await db.rollback()
        raise CommentCreateException()



async def get_comments_with_status_pending(
    db: AsyncSession, skip: int = 0, limit: int = 10
):
    try:
        stmt = (
            select(models.Comment)
            .options(selectinload(models.Comment.comment_icons))
            .where(models.Comment.status == "pending")
            .order_by(models.Comment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        comments = result.unique().scalars().all()

        if not comments:
            return []

        for comment in comments:
            if comment.images is None:
                comment.images = []
            else:
                comment.images = await get_images_with_ids(comment.images)
            
            # Processar ícones de comentário para obter signed URLs
            for icon in _safe_list(getattr(comment, "comment_icons", None)):
                    if icon.icon_url:
                        signed_urls = await get_signed_urls([icon.icon_url])
                        if signed_urls:
                            icon.icon_url = signed_urls[0]
                            
        log_message(f"{len(comments)} comentários pendentes recuperados com sucesso", level="info", logger_name="acesso_livre_api")
        return comments

    except Exception as e:
        log_message(f"Erro ao buscar comentários pendentes: {str(e)}", level="error", logger_name="acesso_livre_api")
        logger.error("Erro ao buscar comentários pendentes: %s", str(e))
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

        status_value = (
            new_status.status.value
            if hasattr(new_status.status, "value")
            else new_status.status
        )
        if status_value not in ["approved", "rejected"]:
            raise CommentStatusInvalidException(status_value)

        stmt = (
            select(models.Comment)
            .options(
                selectinload(models.Comment.comment_icons)
            )
            .where(models.Comment.id == comment_id)
        )
        result = await db.execute(stmt)
        comment = result.scalars().first()
        logger.info("Comentário encontrado: %s", comment is not None)

        if not comment:
            log_message(f"Comentário {comment_id} não encontrado para atualização", level="error", logger_name="acesso_livre_api")
            raise CommentNotFoundException()

        logger.info("Status atual do comentário: %s", comment.status)
        if comment.status != "pending":
            log_message(f"Comentário {comment_id} não está pendente para atualização", level="error", logger_name="acesso_livre_api")
            raise CommentNotPendingException(comment_id, comment.status)

        comment.status = status_value
        await db.commit()
        # Não é necessário fazer refresh neste ponto

        if status_value == "approved":
            await update_location_average_rating(db, comment.location_id, comment.rating)

            if comment.images and len(comment.images) > 0:
                stmt_location = (
                    select(location_models.Location)
                    .options(selectinload(location_models.Location.images))
                    .where(location_models.Location.id == comment.location_id)
                )
                result_location = await db.execute(stmt_location)
                location = result_location.scalars().first()

                if location:
                    if location.images is None:
                        location.images = []

                    for image_path in comment.images:
                        if image_path not in location.images:
                            location.images.append(image_path)

                await db.commit()

        elif status_value == "rejected":
            # Deletar imagens do storage antes de deletar o comentário
            if comment.images:
                try:
                    await delete_images(comment.images)
                    log_message(f"Imagens do comentário {comment_id} deletadas com sucesso antes de excluir o comentário", level="info", logger_name="acesso_livre_api")
                except Exception as e:
                    logger.warning(
                        "Falha ao deletar imagens do comentário %s: %s. "
                        "Prosseguindo com exclusão do comentário.",
                        comment_id, str(e)
                    )
                    log_message(f"Falha ao deletar imagens do comentário {comment_id}: {str(e)}. Prosseguindo com exclusão do comentário.", level="warning", logger_name="acesso_livre_api")

            # Deletar o comentário do banco de dados
            await db.delete(comment)
            await db.commit()

            logger.info(
                "Comentário %s com status rejected foi deletado com sucesso",
                comment_id,
            )
            log_message(f"Comentário {comment_id} rejeitado e deletado com sucesso", level="info", logger_name="acesso_livre_api")
            return comment

        if comment.images is None:
            comment.images = []
        
        # Processar ícones de comentário para obter signed URLs
        for icon in _safe_list(getattr(comment, "comment_icons", None)):
                if icon.icon_url:
                    signed_urls = await get_signed_urls([icon.icon_url])
                    if signed_urls:
                        icon.icon_url = signed_urls[0]

        logger.info(
            "Comentário %s atualizado com sucesso para status %s",
            comment_id,
            status_value,
        )
        log_message(f"Comentário {comment_id} atualizado com sucesso para status '{status_value}'", level="info", logger_name="acesso_livre_api")
        return comment


    except (
        CommentNotFoundException,
        CommentStatusInvalidException,
        CommentNotPendingException,
    ):
        log_message(f"Falha ao atualizar status do comentário {comment_id}", level="error", logger_name="acesso_livre_api")
        raise
    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error(
            "Erro de banco de dados ao atualizar comentário %s: %s", comment_id, str(e)
        )
        await db.rollback()
        log_message(f"Erro de banco de dados ao atualizar comentário {comment_id}: {str(e)}", level="error", logger_name="acesso_livre_api")
        raise CommentUpdateException()
    except Exception as e:
        logger.error("Erro inesperado ao atualizar comentário %s: %s", comment_id, str(e))
        await db.rollback()
        log_message(f"Erro inesperado ao atualizar comentário {comment_id}: {str(e)}", level="error", logger_name="acesso_livre_api")
        raise CommentUpdateException()


async def delete_comment(
    db: AsyncSession, comment_id: int, user_permissions: bool = True
):
    try:
        if not user_permissions:
            log_message(f"Permissão negada para deletar comentário {comment_id}", level="error", logger_name="acesso_livre_api")
            raise CommentPermissionDeniedException()

        stmt = select(models.Comment).where(models.Comment.id == comment_id)
        result = await db.execute(stmt)
        comment = result.scalars().first()

        if not comment:
            log_message(f"Comentário {comment_id} não encontrado para exclusão", level="error", logger_name="acesso_livre_api")
            raise CommentNotFoundException()

        # Deletar imagens do storage antes de deletar o comentário
        if comment.images:
            try:
                await delete_images(comment.images)
            except Exception as e:
                logger.warning(
                    "Falha ao deletar imagens do comentário %s: %s. "
                    "Prosseguindo com exclusão do comentário.",
                    comment_id, str(e)
                )
                log_message(f"Falha ao deletar imagens do comentário {comment_id}: {str(e)}. Prosseguindo com exclusão do comentário.", level="warning", logger_name="acesso_livre_api")

        await db.delete(comment)
        await db.commit()

        log_message(f"Comentário {comment_id} deletado com sucesso", level="info", logger_name="acesso_livre_api")
        return True

    except (CommentNotFoundException, CommentPermissionDeniedException):
        log_message(f"Falha ao deletar comentário {comment_id}", level="error", logger_name="acesso_livre_api")
        raise
    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error(
            "Erro de banco de dados ao excluir comentário %s: %s", comment_id, str(e)
        )
        await db.rollback()
        log_message(f"Erro de banco de dados ao excluir comentário {comment_id}: {str(e)}", level="error", logger_name="acesso_livre_api")
        raise CommentDeleteException()
    except Exception as e:
        logger.error("Erro inesperado ao excluir comentário %s: %s", comment_id, str(e))
        log_message(f"Erro inesperado ao excluir comentário {comment_id}: {str(e)}", level="error", logger_name="acesso_livre_api")
        await db.rollback()
        raise CommentDeleteException()


async def get_all_comments_by_location_id(
    location_id: int, skip: int, limit: int, db: AsyncSession
):
    try:
        stmt = (
            select(models.Comment)
            .options(selectinload(models.Comment.comment_icons))
            .where(
                models.Comment.location_id == location_id,
                models.Comment.status == "approved",
            )
            .order_by(models.Comment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        comments = result.unique().scalars().all()

        if not comments:
            return []

        for comment in comments:
            if comment.images is None:
                comment.images = []
            else:
                comment.images = await get_images_with_ids(comment.images)
            
            # Processar ícones de comentário para obter signed URLs
            for icon in _safe_list(getattr(comment, "comment_icons", None)):
                    if icon.icon_url:
                        signed_urls = await get_signed_urls([icon.icon_url])
                        if signed_urls:
                            icon.icon_url = signed_urls[0]

        log_message(f"{len(comments)} comentários recuperados para o local {location_id}", level="info", logger_name="acesso_livre_api")
        return comments

    except Exception as e:
        logger.error(
            "Erro ao buscar comentários para o local %s: %s", location_id, str(e)
        )
        log_message(f"Erro ao buscar comentários para o local {location_id}: {str(e)}", level="error", logger_name="acesso_livre_api")
        raise CommentGenericException()


async def get_all_comments_with_accessibility_items(
    location_id: int, skip: int, limit: int, db: AsyncSession
):
    """Buscar comentários aprovados de uma localização com seus itens de acessibilidade.
    
    Retorna uma tupla com (comentários, itens_de_acessibilidade).
    """
    try:
        # Buscar comentários
        stmt = (
            select(models.Comment)
            .options(selectinload(models.Comment.comment_icons))
            .where(
                models.Comment.location_id == location_id,
                models.Comment.status == "approved",
            )
            .order_by(models.Comment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        comments = result.unique().scalars().all()

        # Processar imagens dos comentários
        for comment in comments:
            if comment.images is None:
                comment.images = []
            else:
                comment.images = await get_images_with_ids(comment.images)
            
            # Processar ícones de comentário para obter signed URLs
            for icon in _safe_list(getattr(comment, "comment_icons", None)):
                    if icon.icon_url:
                        signed_urls = await get_signed_urls([icon.icon_url])
                        if signed_urls:
                            icon.icon_url = signed_urls[0]

        # Buscar itens de acessibilidade da localização
        stmt_location = (
            select(location_models.Location)
            .options(selectinload(location_models.Location.accessibility_items))
            .where(location_models.Location.id == location_id)
        )
        result_location = await db.execute(stmt_location)
        location = result_location.scalars().first()
        
        accessibility_items = []
        if location and location.accessibility_items:
            # Converter accessibility_items para lista de dicts
            accessibility_items = [
                {"id": item.id, "name": item.name}
                for item in location.accessibility_items
            ]

        return comments, accessibility_items

    except Exception as e:
        logger.error(
            "Erro ao buscar comentários para o local %s: %s",
            location_id,
            str(e),
        )
        log_message(f"Erro ao buscar comentários para o local {location_id}: {str(e)}", level="error", logger_name="acesso_livre_api")
        raise CommentGenericException()



async def get_recent_comments(db: AsyncSession, limit: int = 3):
    try:
        stmt = (
            select(models.Comment)
            .options(
                selectinload(models.Comment.location),
                selectinload(models.Comment.comment_icons)
            )
            .where(models.Comment.status == "approved")
            .order_by(models.Comment.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        comments = result.unique().scalars().all()

        if not comments:
            return []
        
        for comment in comments:
            if comment.images is None:
                comment.images = []
            else:
                comment.images = await get_signed_urls(comment.images)

            # Campo legado usado em mocks/testes unitários
            if hasattr(comment, "icon_url") and getattr(comment, "icon_url"):
                signed_urls = await get_signed_urls([comment.icon_url])
                if signed_urls:
                    comment.icon_url = signed_urls[0]
            
            for icon in _safe_list(getattr(comment, "comment_icons", None)):
                    if icon.icon_url:
                        signed_urls = await get_signed_urls([icon.icon_url])
                        if signed_urls:
                            icon.icon_url = signed_urls[0]

        log_message(f"{len(comments)} comentários recentes recuperados", level="info", logger_name="acesso_livre_api")
        return comments

    except Exception as e:
        logger.error("Erro ao buscar comentários recentes: %s", str(e))
        log_message(f"Erro ao buscar comentários recentes: {str(e)}", level="error", logger_name="acesso_livre_api")
        raise CommentGenericException()


async def delete_comment_image(
    db: AsyncSession, image_id: str
):
    """Deleta uma imagem específica buscando em todos os comentários.
    
    Args:
        db: Sessão do banco de dados
        image_id: UUID da imagem (extraído do filename, sem extensão)
    
    Raises:
        ImageNotFoundException: Se a imagem não for encontrada em nenhum comentário
        ImageDeleteException: Se houver erro ao deletar a imagem
    """
    try:
        # Buscar todos os comentários que possuem imagens
        stmt = select(models.Comment).where(models.Comment.images.isnot(None))
        result = await db.execute(stmt)
        comments = result.scalars().all()

        # Encontrar o comentário que contém essa imagem
        target_comment = None
        image_path = None
        
        for comment in comments:
            if comment.images:
                found_path = find_image_path_by_id(comment.images, image_id)
                if found_path:
                    target_comment = comment
                    image_path = found_path
                    break

        if not target_comment or not image_path:
            raise ImageNotFoundException(image_id)

        # Deletar do storage
        try:
            await delete_image(image_path)
        except Exception as e:
            logger.warning(
                "Falha ao deletar imagem %s do storage: %s. Prosseguindo com remoção do banco.",
                image_id, str(e)
            )
            log_message(f"Falha ao deletar imagem {image_id} do storage: {str(e)}. Prosseguindo com remoção do banco.", level="warning", logger_name="acesso_livre_api")

        # Remover do array de imagens do comentário
        target_comment.images = [img for img in target_comment.images if img != image_path]
        
        # Também remover da location se existir
        if target_comment.location_id:
            stmt_location = select(location_models.Location).where(
                location_models.Location.id == target_comment.location_id
            )
            result_location = await db.execute(stmt_location)
            location = result_location.scalars().first()
            
            if location and location.images:
                location.images = [img for img in location.images if img != image_path]

        await db.commit()
        
        logger.info(
            "Imagem %s deletada com sucesso do comentário %s",
            image_id, target_comment.id
        )
        
        log_message(f"Imagem {image_id} deletada com sucesso do comentário {target_comment.id}", level="info", logger_name="acesso_livre_api")
        return True

    except ImageNotFoundException:
        log_message(f"Imagem {image_id} não encontrada para deleção", level="error", logger_name="acesso_livre_api")
        raise
    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error(
            "Erro de banco de dados ao deletar imagem %s: %s", image_id, str(e)
        )
        await db.rollback()
        log_message(f"Erro de banco de dados ao deletar imagem {image_id}: {str(e)}", level="error", logger_name="acesso_livre_api")
        raise ImageDeleteException(image_id)
    except Exception as e:
        logger.error("Erro inesperado ao deletar imagem %s: %s", image_id, str(e))
        await db.rollback()
        log_message(f"Erro inesperado ao deletar imagem {image_id}: {str(e)}", level="error", logger_name="acesso_livre_api")
        raise ImageDeleteException(image_id)


# Comment Icon Management Functions

async def create_comment_icon(db: AsyncSession, name: str, icon_url: str):
    """Criar um novo ícone de comentário."""
    try:
        db_icon = models.CommentIcon(name=name, icon_url=icon_url)
        db.add(db_icon)
        await db.commit()
        await db.refresh(db_icon)
        
        log_message(f"Novo ícone de comentário criado: {name}", level="info", logger_name="acesso_livre_api")
        return db_icon

    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error("Erro de banco de dados ao criar ícone de comentário: %s", str(e))
        await db.rollback()
        log_message(f"Erro de banco de dados ao criar ícone de comentário: {str(e)}", level="error", logger_name="acesso_livre_api")
        raise CommentGenericException()
    except Exception as e:
        logger.error("Erro inesperado ao criar ícone de comentário: %s", str(e))
        await db.rollback()
        log_message(f"Erro inesperado ao criar ícone de comentário: {str(e)}", level="error", logger_name="acesso_livre_api")
        raise CommentGenericException()


async def get_all_comment_icons(db: AsyncSession):
    """Obter todos os ícones de comentário com signed URLs."""
    try:
        stmt = select(models.CommentIcon)
        result = await db.execute(stmt)
        icons = result.scalars().all()

        # Obter signed URLs para os ícones
        icon_urls = [icon.icon_url for icon in icons if icon.icon_url]
        signed_urls_list = await get_signed_urls(icon_urls) if icon_urls else []

        # Mapear icon_url para signed_url
        icon_url_mapping = dict(zip(icon_urls, signed_urls_list))

        # Atualizar os ícones com signed URLs
        for icon in icons:
            if icon.icon_url in icon_url_mapping:
                icon.icon_url = icon_url_mapping[icon.icon_url]

        return icons

    except Exception as e:
        logger.error("Erro ao obter ícones de comentário: %s", str(e))
        log_message(f"Erro ao obter ícones de comentário: {str(e)}", level="error", logger_name="acesso_livre_api")
        raise CommentGenericException()


async def get_comment_icon_by_id(db: AsyncSession, icon_id: int):
    """Obter um ícone de comentário pelo ID."""
    try:
        stmt = select(models.CommentIcon).where(models.CommentIcon.id == icon_id)
        result = await db.execute(stmt)
        icon = result.scalars().first()

        if not icon:
            raise CommentGenericException()

        # Obter signed URL
        if icon.icon_url:
            signed_urls = await get_signed_urls([icon.icon_url])
            if signed_urls:
                icon.icon_url = signed_urls[0]

        return icon

    except Exception as e:
        logger.error("Erro ao obter ícone de comentário %s: %s", icon_id, str(e))
        log_message(f"Erro ao obter ícone de comentário {icon_id}: {str(e)}", level="error", logger_name="acesso_livre_api")
        raise CommentGenericException()


async def update_comment_icon(
    db: AsyncSession,
    icon_id: int,
    name: str | None = None,
    image: UploadFile | None = None,
):
    """Atualizar um ícone de comentário."""
    try:
        stmt = select(models.CommentIcon).where(models.CommentIcon.id == icon_id)
        result = await db.execute(stmt)
        icon = result.scalars().first()

        if not icon:
            raise CommentGenericException()

        if name:
            icon.name = name

        if image:
            # Upload da nova imagem
            new_icon_url = await upload_image.upload_image(image)

            # Deletar imagem antiga se existir
            if icon.icon_url:
                try:
                    await delete_image(icon.icon_url)
                except Exception as e:
                    logger.warning(
                        "Falha ao deletar imagem antiga %s do ícone %s: %s",
                        icon.icon_url,
                        icon_id,
                        str(e),
                    )
                    log_message(
                        f"Falha ao deletar imagem antiga {icon.icon_url} do ícone {icon_id}: {str(e)}",
                        level="warning",
                        logger_name="acesso_livre_api",
                    )

            icon.icon_url = new_icon_url

        await db.commit()
        await db.refresh(icon)

        # Obter signed URL para retorno
        if icon.icon_url:
            signed_urls = await get_signed_urls([icon.icon_url])
            if signed_urls:
                icon.icon_url = signed_urls[0]

        log_message(
            f"Ícone de comentário {icon_id} atualizado com sucesso",
            level="info",
            logger_name="acesso_livre_api",
        )
        return icon

    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error(
            "Erro de banco de dados ao atualizar ícone de comentário %s: %s",
            icon_id,
            str(e),
        )
        await db.rollback()
        log_message(
            f"Erro de banco de dados ao atualizar ícone de comentário {icon_id}: {str(e)}",
            level="error",
            logger_name="acesso_livre_api",
        )
        raise CommentGenericException()
    except Exception as e:
        logger.error(
            "Erro inesperado ao atualizar ícone de comentário %s: %s", icon_id, str(e)
        )
        await db.rollback()
        log_message(
            f"Erro inesperado ao atualizar ícone de comentário {icon_id}: {str(e)}",
            level="error",
            logger_name="acesso_livre_api",
        )
        raise CommentGenericException()


async def delete_comment_icon(db: AsyncSession, icon_id: int):
    """Deletar um ícone de comentário."""
    try:
        stmt = select(models.CommentIcon).where(models.CommentIcon.id == icon_id)
        result = await db.execute(stmt)
        icon = result.scalars().first()

        if not icon:
            raise CommentGenericException()

        # Tentar deletar do storage
        if icon.icon_url:
            try:
                await delete_image(icon.icon_url)
            except Exception as e:
                logger.warning(
                    "Falha ao deletar ícone %s do storage: %s. Prosseguindo com remoção do banco.",
                    icon_id, str(e)
                )
                log_message(f"Falha ao deletar ícone {icon_id} do storage: {str(e)}. Prosseguindo com remoção do banco.", level="warning", logger_name="acesso_livre_api")

        await db.delete(icon)
        await db.commit()
        
        log_message(f"Ícone de comentário {icon_id} deletado com sucesso", level="info", logger_name="acesso_livre_api")
        return True

    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error("Erro de banco de dados ao deletar ícone de comentário %s: %s", icon_id, str(e))
        await db.rollback()
        log_message(f"Erro de banco de dados ao deletar ícone de comentário {icon_id}: {str(e)}", level="error", logger_name="acesso_livre_api")
        raise CommentGenericException()
    except Exception as e:
        logger.error("Erro inesperado ao deletar ícone de comentário %s: %s", icon_id, str(e))
        await db.rollback()
        log_message(f"Erro inesperado ao deletar ícone de comentário {icon_id}: {str(e)}", level="error", logger_name="acesso_livre_api")
        raise CommentGenericException()
