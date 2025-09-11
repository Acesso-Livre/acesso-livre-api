from typing import Union
from fastapi import FastAPI
from .config import settings

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": settings.api}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}