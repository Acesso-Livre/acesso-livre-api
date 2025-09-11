from typing import Union
from fastapi import FastAPI
from .database import Base, engine, get_db
from .config import settings
from .comments.router import router as comments_router

app = FastAPI()

Base.metadata.create_all(bind=engine)


app.include_router(comments_router, prefix="/api/comments", tags=["comments"])

@app.get("/")
def read_root():
    return {"Hello": settings.api}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}