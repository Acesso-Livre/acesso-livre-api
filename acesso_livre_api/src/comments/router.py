from fastapi import APIRouter, Depends, status
from fastapi.params import Query
from sqlalchemy.orm import Session

from acesso_livre_api.src.admins import dependencies
from acesso_livre_api.src.comments import docs, schemas, service
from acesso_livre_api.src.comments.exceptions import (
    CommentCreateException,
    CommentNotFoundException,
)
from acesso_livre_api.src.database import get_db
from acesso_livre_api.src.locations.exceptions import LocationNotFoundException

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.CommentCreateResponse,
    **docs.CREATE_COMMENT_DOCS,
)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    try:
        new_comment = service.create_comment(db=db, comment=comment)
    except LocationNotFoundException:
        raise
    except Exception as e:
        raise CommentCreateException(str(e))
    return new_comment


@router.get(
    "/pending",
    response_model=schemas.CommentListResponse,
    **docs.GET_PENDING_COMMENTS_DOCS,
)
@dependencies.require_auth
def get_comments_with_status_pending(
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(
        10, ge=1, le=10, description="Número máximo de registros a retornar"
    ),
    db: Session = Depends(get_db),
    authenticated_user: bool = dependencies.authenticated_user,
):
    db_comments = service.get_comments_with_status_pending(db, skip=skip, limit=limit)
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
@dependencies.require_auth
def get_all_comments_by_location_id(
    location_id: int,
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(
        10, ge=1, le=10, description="Número máximo de registros a retornar"
    ),
    authenticated_user: bool = dependencies.authenticated_user,
    db: Session = Depends(get_db),
):

    db_comments = service.get_all_comments_by_location_id(location_id, skip, limit, db)

    comments = [
        schemas.CommentResponse.model_validate(comment) for comment in db_comments
    ]

    return schemas.CommentListByLocationResponse(comments=comments)


@router.patch(
    "/{comment_id}/status",
    response_model=schemas.CommentResponseOnlyStatusPending,
    **docs.UPDATE_COMMENT_STATUS_DOCS,
)
@dependencies.require_auth
def update_comment_status_with_id(
    comment_id: int,
    new_status: schemas.CommentUpdateStatus,
    db: Session = Depends(get_db),
    authenticated_user: bool = dependencies.authenticated_user,
):
    updated_comment = service.update_comment_status(db, comment_id, new_status)
    return updated_comment


@router.delete("/{comment_id}", **docs.DELETE_COMMENT_DOCS)
@dependencies.require_auth
def delete_comment_with_id(
    comment_id: int,
    db: Session = Depends(get_db),
    authenticated_user: bool = dependencies.authenticated_user,
):
    success = service.delete_comment(
        db, comment_id, user_permissions=authenticated_user
    )
    if not success:
        raise CommentNotFoundException()
    return {"detail": "Comment deleted successfully"}


@router.get(
    "/{comment_id}",
    response_model=schemas.CommentResponseWithLocationId,
    **docs.GET_COMMENT_DOCS,
)
def read_comment(comment_id: int, db: Session = Depends(get_db)):
    db_comment = service.get_comment(db, comment_id)
    if db_comment is None:
        raise CommentNotFoundException()
    return db_comment
