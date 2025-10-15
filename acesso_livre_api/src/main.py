from typing import Union
import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .database import Base, engine
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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Manipulador para capturar erros de validação do Pydantic (422) e
    retornar um erro padronizado 500
    """
    logging.error(f"Erro de validação de dados: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno ao processar solicitação"},
    )

# Configuração OpenAPI obrigatória com autenticação JWT
app.openapi = create_custom_openapi(app)

Base.metadata.create_all(bind=engine)

app.include_router(admins_router, prefix="/api/admins",tags=["Administração"])
app.include_router(comments_router, prefix="/api/comments", tags=["comments"])

@app.get("/", tags=["Status"])
def read_root():
    return {"status": "active"}