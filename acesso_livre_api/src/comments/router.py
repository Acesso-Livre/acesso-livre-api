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
    accessibility_item_ids: str = Form(None, description="IDs dos itens de acessibilidade separados por vírgula (ex: 1,2,3)"),
    images: list[UploadFile] | None = File(None),
    db: Session = Depends(get_db),
):
    try:
        # Converter string de IDs para lista de inteiros
        parsed_accessibility_ids = None
        if accessibility_item_ids:
            try:
                parsed_accessibility_ids = [
                    int(id.strip()) for id in accessibility_item_ids.split(",") if id.strip()
                ]
            except ValueError:
                raise CommentCreateException(reason="IDs de acessibilidade inválidos")

        comment_data = schemas.CommentCreate(
            user_name=user_name,
            rating=rating,
            comment=comment,
            location_id=location_id,
            accessibility_item_ids=parsed_accessibility_ids,
        )

        await location_service.get_location_by_id(db, location_id)

        new_comment = await service.create_comment(
            db=db, comment=comment_data, images=images
        )
        return new_comment
    except (LocationNotFoundException, CommentRatingInvalidException):
        raise
    except Exception as e:
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

    db_comments, accessibility_items = await service.get_all_comments_with_accessibility_items(
        location_id, skip, limit, db
    )

    comments = [
        schemas.CommentResponse.model_validate(comment) for comment in db_comments
    ]

    return schemas.CommentListByLocationResponse(
        comments=comments, accessibility_items=accessibility_items
    )


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
        raise
    except Exception:
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
        return {"detail": "Comment deleted successfully"}
    except (CommentNotFoundException, CommentPermissionDeniedException):
        raise
    except Exception:
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
        return schemas.RecentCommentsListResponse(comments=comments)
    except Exception as e:
        raise CommentGenericException()


@router.get(
    "/{comment_id}",
    response_model=schemas.CommentResponseWithLocationId,
    **docs.GET_COMMENT_DOCS,
)
async def read_comment(comment_id: int, db: Session = Depends(get_db)):
    try:
        db_comment = await service.get_comment(db, comment_id)
        return db_comment
    except CommentNotFoundException:
        raise
