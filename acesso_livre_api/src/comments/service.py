import logging
from datetime import UTC, datetime

from sqlalchemy import exc as sqlalchemy_exc
from sqlalchemy.orm import Session

from acesso_livre_api.src.comments import models, schemas

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

logger = logging.getLogger(__name__)


def get_comment(db: Session, comment_id: int):
    try:
        comment = (
            db.query(models.Comment)
            .filter(models.Comment.id == comment_id, models.Comment.status == "approved")
            .first()
        )

        if not comment:
            raise CommentNotFoundException()

        if comment.images is None:
            comment.images = []

        return comment

    except CommentNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter comentário {comment_id}: {str(e)}")
        raise CommentNotFoundException()


def create_comment(db: Session, comment: schemas.CommentCreate):
    try:
        if comment.rating < 1 or comment.rating > 5:
            raise CommentRatingInvalidException(comment.rating)

        data = comment.model_dump()
        if not data["images"]:
            data["images"] = []

        if data["images"]:
            for img in data["images"]:
                if not isinstance(img, str) or not img.strip():
                    raise CommentImagesInvalidException(
                        "Uma ou mais imagens têm formato inválido"
                    )

        db_comment = models.Comment(**data, created_at=datetime.now(UTC))
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)

        return db_comment

    except (CommentRatingInvalidException, CommentImagesInvalidException):
        raise
    except Exception as e:
        logger.error(f"Erro ao criar comentário: {str(e)}")
        db.rollback()
        raise CommentCreateException()


def get_comments_with_status_pending(db: Session, skip: int = 0, limit: int = 10):
    try:
        comments = (
            db.query(models.Comment)
            .filter(models.Comment.status == "pending")
            .order_by(models.Comment.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        if not comments:
            return []

        for comment in comments:
            if comment.images is None:
                comment.images = []

        return comments

    except Exception as e:
        logger.error(f"Erro ao buscar comentários pendentes: {str(e)}")
        raise CommentGenericException()


def update_comment_status(
    db: Session, comment_id: int, new_status: schemas.CommentUpdateStatus
):
    try:
        logger.info(
            f"Tentando atualizar comentário {comment_id} para status {new_status.status.value}"
        )

        status_value = (
            new_status.status.value
            if hasattr(new_status.status, "value")
            else new_status.status
        )
        if status_value not in ["approved", "rejected"]:
            raise CommentStatusInvalidException(status_value)

        comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
        logger.info(f"Comentário encontrado: {comment is not None}")

        if not comment:
            raise CommentNotFoundException()

        logger.info(f"Status atual do comentário: {comment.status}")
        if comment.status != "pending":
            raise CommentNotPendingException(comment_id, comment.status)

        comment.status = new_status.status.value
        db.commit()
        db.refresh(comment)

        if comment.images is None:
            comment.images = []

        logger.info(
            f"Comentário {comment_id} atualizado com sucesso para status {new_status.status.value}"
        )
        return comment

    except (
        CommentNotFoundException,
        CommentStatusInvalidException,
        CommentNotPendingException,
    ):
        raise
    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error(
            f"Erro de banco de dados ao atualizar comentário {comment_id}: {str(e)}"
        )
        db.rollback()
        raise CommentUpdateException()
    except Exception as e:
        logger.error(f"Erro inesperado ao atualizar comentário {comment_id}: {str(e)}")
        db.rollback()
        raise CommentUpdateException()


def delete_comment(db: Session, comment_id: int, user_permissions: bool = True):
    try:
        if not user_permissions:
            raise CommentPermissionDeniedException("excluir")

        comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()

        if not comment:
            raise CommentNotFoundException()

        db.delete(comment)
        db.commit()

        return True

    except (CommentNotFoundException, CommentPermissionDeniedException):
        raise
    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error(
            f"Erro de banco de dados ao excluir comentário {comment_id}: {str(e)}"
        )
        db.rollback()
        raise CommentDeleteException()
    except Exception as e:
        logger.error(f"Erro inesperado ao excluir comentário {comment_id}: {str(e)}")
        db.rollback()
        raise CommentDeleteException()


def get_all_comments_by_location_id(location_id: int, skip: int, limit: int, db: Session):
    try:
        comments = (
            db.query(models.Comment)
            .filter(
                models.Comment.location_id == location_id,
                models.Comment.status == "approved",
            )
            .order_by(models.Comment.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        if not comments:
            return []

        for comment in comments:
            if comment.images is None:
                comment.images = []

        return comments

    except Exception as e:
        logger.error(f"Erro ao buscar comentários para o local {location_id}: {str(e)}")
        raise CommentGenericException()
