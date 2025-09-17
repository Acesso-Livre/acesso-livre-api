from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, timezone

def get_comment(db: Session, comment_id: int):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if comment:
        if isinstance(comment.images, str):
            images = comment.images.strip("{} ").split(",") if comment.images else []
            comment.images = [img.strip() for img in images if img.strip()]
        elif comment.images is None:
            comment.images = []
    return comment

def create_comment(db: Session, comment: schemas.CommentCreate):
    images = comment.images
    if isinstance(images, str):
        images = images.strip("{} ").split(",") if images else []
        images = [img.strip() for img in images if img.strip()]
    data = comment.model_dump()
    data["images"] = ",".join(images) if images else None
    db_comment = models.Comment(**data, created_at=datetime.now(timezone.utc))
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment
