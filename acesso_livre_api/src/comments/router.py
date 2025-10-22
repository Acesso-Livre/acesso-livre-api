from fastapi import APIRouter, Depends, HTTPException
from acesso_livre_api.src.admins import dependencies
from sqlalchemy.orm import Session
from . import service, schemas
from ..database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.CommentCreateResponse)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    comment = service.create_comment(db=db, comment=comment)
    if not comment:
        raise HTTPException(status_code=400, detail="Error creating comment")
    return comment

@router.get("/pending", response_model=schemas.CommentListResponse)
@dependencies.require_auth
def get_comments_with_status_pending(
    db: Session = Depends(get_db),
    authenticated_user: bool = dependencies.authenticated_user
):
    db_comments = service.get_comments_with_status_pending(db)
    if not db_comments:
        raise HTTPException(status_code=404, detail="Nenhum comentário pendente encontrado")
    
    comments = [schemas.CommentResponseOnlyStatusPending.model_validate(comment) for comment in db_comments]
    return schemas.CommentListResponse(comments=comments)

@router.patch("/{comment_id}/status", response_model=schemas.CommentResponseOnlyStatusPending)
@dependencies.require_auth
def update_comment_status_with_id(
    comment_id: int,
    new_status: schemas.CommentUpdateStatus,
    db: Session = Depends(get_db),
    authenticated_user: bool = dependencies.authenticated_user
):
    updated_comment = service.update_comment_status(db, comment_id, new_status)
    if updated_comment is None:
        raise HTTPException(status_code=404, detail="Comentário não encontrado ou status não pode ser atualizado")
    return updated_comment

@router.delete("/{comment_id}")
@dependencies.require_auth
def delete_comment_with_id(
    comment_id: int,
    db: Session = Depends(get_db),
    authenticated_user: bool = dependencies.authenticated_user
):
    success = service.delete_comment(db, comment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"detail": "Comment deleted successfully"}

@router.get("/{comment_id}", response_model=schemas.CommentResponseWithLocationId)
def read_comment(comment_id: int, db: Session = Depends(get_db)):
    db_comment = service.get_comment(db, comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment
