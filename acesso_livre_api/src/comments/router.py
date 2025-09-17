from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import service, schemas
from ..database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.CommentCreateResponse)
def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    return service.create_comment(db=db, comment=comment)

@router.get("/{comment_id}", response_model=schemas.CommentResponseWithLocationId)
def read_comment(comment_id: int, db: Session = Depends(get_db)):
    db_comment = service.get_comment(db, comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment
