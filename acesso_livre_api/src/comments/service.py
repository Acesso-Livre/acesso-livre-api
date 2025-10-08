from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, timezone

def get_comment(db: Session, comment_id: int):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if comment and comment.images is None:
        comment.images = []
    return comment

def create_comment(db: Session, comment: schemas.CommentCreate):
    data = comment.model_dump()
    if not data["images"]:
        data["images"] = []
    db_comment = models.Comment(**data, created_at=datetime.now(timezone.utc))
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comments_with_status_pending(db:Session):
    comments = db.query(models.Comment).filter(models.Comment.status == 'pending').all()
    for comment in comments:
        if comment.images is None:
            comment.images = []
    return comments

def update_comment_status(db: Session, comment_id: int, new_status: schemas.CommentUpdateStatus):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if comment and new_status.status in ["approved", "rejected"]:
        comment.status = new_status.status
        db.commit()
        db.refresh(comment)
        if comment.images is None:
            comment.images = []
    else:
        comment = None
    return comment

def delete_comment(db: Session, comment_id: int):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if comment:
        db.delete(comment)
        db.commit()
        return True
    return False