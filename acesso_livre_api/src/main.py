from typing import Union
import logging
from fastapi import FastAPI
from .database import Base, engine, get_db
from .config import settings
from .comments.router import router as comments_router
from .admins.router import router as admins_router
from .openapi_config import create_custom_openapi

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI()

# Configuração OpenAPI obrigatória com autenticação JWT
app.openapi = create_custom_openapi(app)

Base.metadata.create_all(bind=engine)

app.include_router(admins_router, prefix="/api/admins", tags=["admins"])
app.include_router(comments_router, prefix="/api/comments", tags=["comments"])

@app.get("/")
def read_root():
    return {"Hello": settings.api}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str | None] = None):
    return {"item_id": item_id, "q": q}