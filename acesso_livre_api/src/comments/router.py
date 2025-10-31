from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from acesso_livre_api.src.admins import dependencies

from ..database import get_db
from . import docs, schemas, service
from .exceptions import (
    CommentCreateException,
    CommentNotFoundException,
)

router = APIRouter()

@router.post("/", response_model=schemas.CommentCreateResponse, **docs.CREATE_COMMENT_DOCS)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    comment = service.create_comment(db=db, comment=comment)
    if not comment:
        raise CommentCreateException("Error creating comment")
    return comment

@router.get("/pending", response_model=schemas.CommentListResponse, **docs.GET_PENDING_COMMENTS_DOCS)
@dependencies.require_auth
def get_comments_with_status_pending(
    db: Session = Depends(get_db),
    authenticated_user: bool = dependencies.authenticated_user
):
    db_comments = service.get_comments_with_status_pending(db)
    comments = [schemas.CommentResponseOnlyStatusPending.model_validate(comment) for comment in db_comments]
    return schemas.CommentListResponse(comments=comments)

@router.patch("/{comment_id}/status", response_model=schemas.CommentResponseOnlyStatusPending, **docs.UPDATE_COMMENT_STATUS_DOCS)
@dependencies.require_auth
def update_comment_status_with_id(
    comment_id: int,
    new_status: schemas.CommentUpdateStatus,
    db: Session = Depends(get_db),
    authenticated_user: bool = dependencies.authenticated_user
):
    updated_comment = service.update_comment_status(db, comment_id, new_status)
    if updated_comment is None:
        raise CommentNotFoundException()
    return updated_comment

@router.delete("/{comment_id}", **docs.DELETE_COMMENT_DOCS)
@dependencies.require_auth
def delete_comment_with_id(
    comment_id: int,
    db: Session = Depends(get_db),
    authenticated_user: bool = dependencies.authenticated_user
):
    success = service.delete_comment(db, comment_id, user_permissions=authenticated_user)
    if not success:
        raise CommentNotFoundException()
    return {"detail": "Comment deleted successfully"}

@router.get("/{comment_id}", response_model=schemas.CommentResponseWithLocationId, **docs.GET_COMMENT_DOCS)
def read_comment(comment_id: int, db: Session = Depends(get_db)):
    db_comment = service.get_comment(db, comment_id)
    if db_comment is None:
        raise CommentNotFoundException()
    return db_comment
