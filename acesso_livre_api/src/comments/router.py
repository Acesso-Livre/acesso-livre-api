from fastapi import APIRouter, Depends, File, UploadFile, Form, status
from fastapi.params import Query
from sqlalchemy.orm import Session

from acesso_livre_api.src.admins import dependencies
from acesso_livre_api.src.comments import docs, schemas, service
from acesso_livre_api.src.comments.exceptions import (
    CommentCreateException,
    CommentDeleteException,
    CommentGenericException,
    CommentNotFoundException,
    CommentNotPendingException,
    CommentPermissionDeniedException,
    CommentRatingInvalidException,
    CommentStatusInvalidException,
    CommentUpdateException,
)
from acesso_livre_api.src.database import get_db
from acesso_livre_api.src.locations import service as location_service
from acesso_livre_api.src.locations.exceptions import LocationNotFoundException
from acesso_livre_api.storage import upload_image

from func_log import *

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.CommentCreateResponse,
    **docs.CREATE_COMMENT_DOCS,
)
async def create_comment(
    user_name: str = Form(..., max_length=30),
    rating: int = Form(..., ge=1, le=5),
    comment: str = Form(..., max_length=500),
    location_id: int = Form(...),
    images: list[UploadFile] | None = File(None),
    db: Session = Depends(get_db),
):
    try:
        comment_data = schemas.CommentCreate(
            user_name=user_name, rating=rating, comment=comment, location_id=location_id
        )

        await location_service.get_location_by_id(db, location_id)

        new_comment = await service.create_comment(
            db=db, comment=comment_data, images=images
        )
        log_message(f"Comentário criado com sucesso para o local {location_id} por {user_name}", level="info")
        return new_comment
    except (LocationNotFoundException, CommentRatingInvalidException):
        log_message(f"Falha ao criar comentário para o local {location_id} por {user_name}", level="warning")
        raise
    except Exception as e:
        log_message(f"Erro ao criar comentário para o local {location_id} por {user_name}", level="error")
        log_message(str(e), level="error")
        raise CommentCreateException(reason=str(e))


@router.get(
    "/pending",
    response_model=schemas.CommentListResponse,
    **docs.GET_PENDING_COMMENTS_DOCS,
)
@dependencies.require_auth
async def get_comments_with_status_pending(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(
        10, ge=1, le=10, description="Número máximo de registros a retornar"
    ),
    db: Session = Depends(get_db),
    authenticated_user: bool = dependencies.authenticated_user,
):
    db_comments = await service.get_comments_with_status_pending(db, skip, limit)
    comments = [
        schemas.CommentResponseOnlyStatusPending.model_validate(comment)
        for comment in db_comments
    ]
    log_message(f"Recuperados {len(comments)} comentários pendentes", level="info")
    return schemas.CommentListResponse(comments=comments)


@router.get(
    "/{location_id}/comments",
    response_model=schemas.CommentListByLocationResponse,
    **docs.GET_COMMENTS_BY_LOCATION_DOCS,
)
async def get_all_comments_by_location_id(
    location_id: int,
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(
        10, ge=1, le=10, description="Número máximo de registros a retornar"
    ),
    db: Session = Depends(get_db),
):

    db_comments = await service.get_all_comments_by_location_id(
        location_id, skip, limit, db
    )

    comments = [
        schemas.CommentResponse.model_validate(comment) for comment in db_comments
    ]
    log_message(f"Recuperados {len(comments)} comentários para o local {location_id}", level="info")
    return schemas.CommentListByLocationResponse(comments=comments)


@router.patch(
    "/{comment_id}/status",
    response_model=schemas.CommentResponseOnlyStatusPending,
    **docs.UPDATE_COMMENT_STATUS_DOCS,
)
@dependencies.require_auth
async def update_comment_status_with_id(
    comment_id: int,
    new_status: schemas.CommentUpdateStatus,
    db: Session = Depends(get_db),
    authenticated_user: bool = dependencies.authenticated_user,
):
    try:
        updated_comment = await service.update_comment_status(db, comment_id, new_status)
        return updated_comment
    except (
        CommentNotFoundException,
        CommentNotPendingException,
        CommentStatusInvalidException,
    ):
        log_message(f"Falha ao atualizar status do comentário {comment_id}", level="warning")
        raise
    except Exception:
        log_message(f"Erro ao atualizar status do comentário {comment_id}", level="error")
        raise CommentUpdateException(comment_id=comment_id)


@router.delete("/{comment_id}", **docs.DELETE_COMMENT_DOCS)
@dependencies.require_auth
async def delete_comment_with_id(
    comment_id: int,
    db: Session = Depends(get_db),
    authenticated_user: bool = dependencies.authenticated_user,
):
    try:
        await service.delete_comment(db, comment_id, user_permissions=authenticated_user)
        log_message(f"Comentário {comment_id} excluído com sucesso", level="info")
        return {"detail": "Comment deleted successfully"}
    except (CommentNotFoundException, CommentPermissionDeniedException):
        log_message(f"Falha ao excluir comentário {comment_id}", level="warning")
        raise
    except Exception:
        log_message(f"Erro ao excluir comentário {comment_id}", level="error")
        raise CommentDeleteException()


@router.get(
    "/recent",
    response_model=schemas.RecentCommentsListResponse,
    **docs.GET_RECENT_COMMENTS_DOCS,
)
async def get_recent_comments(
    limit: int = Query(
        3, ge=1, le=10, description="Número máximo de comentários recentes a retornar"
    ),
    db: Session = Depends(get_db),
):
    try:
        db_comments = await service.get_recent_comments(db, limit)
        comments = [
            schemas.RecentCommentResponse(
                location_name=comment.location.name,
                location_rating=comment.location.avg_rating or 0.0,
                user_name=comment.user_name,
                description=comment.comment,
            )
            for comment in db_comments
        ]
        log_message(f"Recuperados {len(comments)} comentários recentes", level="info")
        return schemas.RecentCommentsListResponse(comments=comments)
    except Exception as e:
        log_message("Erro ao recuperar comentários recentes", level="error")
        log_message(str(e), level="error")
        raise CommentGenericException()


@router.get(
    "/{comment_id}",
    response_model=schemas.CommentResponseWithLocationId,
    **docs.GET_COMMENT_DOCS,
)
async def read_comment(comment_id: int, db: Session = Depends(get_db)):
    try:
        db_comment = await service.get_comment(db, comment_id)
        log_message(f"Comentário {comment_id} recuperado com sucesso", level="info")
        return db_comment
    except CommentNotFoundException:
        log_message(f"Comentário {comment_id} não encontrado", level="warning")
        raise
