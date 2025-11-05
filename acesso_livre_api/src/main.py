import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .admins.router import router as admins_router
from .comments.router import router as comments_router
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
    retornar uma resposta JSON estruturada e amigável.
    """
    # Verificar se há erros de path params
    has_path_errors = any('path' in str(error["loc"]) for error in exc.errors())
    
    if has_path_errors:
        # Retornar resposta minificada para erros de path params
        logging.error(f"Erro de validação de path params: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "detail": "Parâmetro de rota inválido",
            },
        )
    
    # Formato detalhado para erros de body/request
    formatted_errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if str(loc) != 'body')
        message = error["msg"]
        formatted_errors.append({"field": field, "message": message})

    logging.error(f"Erro de validação de dados: {formatted_errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "detail": "Ocorreram erros de validação.",
            "errors": formatted_errors,
        },
    )

# Configuração OpenAPI obrigatória com autenticação JWT
app.openapi = create_custom_openapi(app)

app.include_router(admins_router, prefix="/api/admins",tags=["Administração"])
app.include_router(comments_router, prefix="/api/comments", tags=["comments"])

@app.get("/", tags=["Status"])
def read_root():
    return {"status": "active"}
